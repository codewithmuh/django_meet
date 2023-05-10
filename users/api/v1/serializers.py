from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists, generate_unique_username
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers, exceptions
from rest_auth.models import TokenModel
from users.models import UserSignupCode
from users.utils import get_random_str

if settings.DRF_RECAPTCHA_SECRET_KEY:
    from drf_recaptcha.fields import ReCaptchaV2Field

User = get_user_model()


class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(error_messages={
        'blank': _("Please provide phone number."), }, write_only=True)


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, error_messages={
        'blank': _("Please provide Email Address."), })
    if settings.DRF_RECAPTCHA_SECRET_KEY:
        recaptcha = ReCaptchaV2Field(error_messages={
            'blank': _("Please check off the ReCaptcha box to confirm that you're not a robot."), })

    class Meta:
        model = User
        if settings.DRF_RECAPTCHA_SECRET_KEY:
            fields = ("id",  'first_name', 'last_name',
                      'dob', "email", "password", "recaptcha")
        else:
            fields = ("id", 'first_name', 'last_name',
                      'dob', "email", "password")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "email": {"required": True, "allow_blank": False, }}

    def _get_request(self):
        request = self.context.get("request")
        if (
                request
                and not isinstance(request, HttpRequest)
                and hasattr(request, "_request")
        ):
            request = request._request
        return request

    def validate(self, attrs):
        email = attrs.get("email")
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    {"email": _(
                        "A user is already registered with this e-mail address.")}
                )

        validated_data = super().validate(attrs)

        password = validated_data.get("password")
        # Check if password is at least 8 characters long
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long.")

        # Check if password contains uppercase and lowercase letters, and at least one digit
        if not any(c.isupper() for c in password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in password):
            raise ValidationError(
                "Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit.")

        return validated_data

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        return email

    @transaction.atomic()
    def create(self, validated_data):
        user = User(
            email=validated_data.get("email"),
            username=generate_unique_username(
                [validated_data.get("name"), validated_data.get(
                    "email"), "user"]
            ),
        )
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        dob = validated_data.get("dob")
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if dob:
            user.dob = dob
        if first_name and last_name:
            user.name = f'{validated_data.get("first_name")} {validated_data.get("last_name")}'

        user.set_password(validated_data.get("password"))
        user.save()
        request = self._get_request()
        setup_user_email(request, user, [])
        try:
            self.send_code_email(user)
        except Exception as e:
            raise serializers.ValidationError(
                {"message": _(f"error while sending email {e}")}
            )
        return user

    def send_code_email(self, user):
        code = get_random_str(6)
        while UserSignupCode.objects.filter(code=code).exists():
            code = get_random_str(6)
        user_code = UserSignupCode.objects.filter(email=user.email).first()
        if user_code:
            user_code.code = code
            user_code.save()
        else:
            UserSignupCode.objects.create(email=user.email, code=code)

        message = ""
        html_message = render_to_string(
            "account/email/confirmation.html", {"code": code})
        send_mail(
            'Medas insurance confirmation code',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
        print("send email key.")

    def save(self, request=None):
        """rest_auth passes request so we must override to accept it"""
        return super().save()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", 'first_name', 'last_name', "name", 'passport_no', 'nationality', 'dob', 'gender', 'image'
                  ]
        extra_kwargs = {
            "email": {
                "read_only": True
            },
        }

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class CustomTokenSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta:
        model = TokenModel
        fields = ('key', "user_detail")


class VerifyUserSignupCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class ResendUserSignupEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': _('Please make sure you have entered correct credentials.'),
        'not_verified': _('Please verify your email first.')
    }
    if settings.DRF_RECAPTCHA_SECRET_KEY:
        recaptcha = ReCaptchaV2Field(error_messages={
            'blank': _("Please check off the ReCaptcha box to confirm that you're not a robot."), })

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        if EmailAddress.objects.filter(user=self.user, email=self.user.email, verified=False).exists():
            raise exceptions.AuthenticationFailed(
                self.error_messages["not_verified"],
                "not_verified",
            )
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data["user_detail"] = UserSerializer(
            self.user, many=False, read_only=True).data
        update_last_login(None, self.user)
        return data
