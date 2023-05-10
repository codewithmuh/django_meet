from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status, permissions
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.api.v1.serializers import (
    SignupSerializer,
    UserSerializer,
    VerifyUserSignupCodeSerializer,
    CustomTokenObtainPairSerializer,
    ResendUserSignupEmailSerializer,
)
from users.models import UserSignupCode
from users.utils import get_random_str

User = get_user_model()


# This is a Django REST framework viewset for handling user signups with a serializer class and only
# allowing the HTTP POST method.
class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    queryset = User.objects.none()
    http_method_names = ["post", ]

    def get_serializer_class(self):
        return super(SignupViewSet, self).get_serializer_class()


class VerifyUserSignupCodeViewSet(ListCreateAPIView):
    serializer_class = VerifyUserSignupCodeSerializer
    queryset = UserSignupCode.objects.none()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response()

    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get("code")
        user_code = UserSignupCode.objects.filter(code=code)
        if user_code:
            email = user_code.first().email
            EmailAddress.objects.filter(email__exact=email).update(verified=True)
            user_code.delete()
            user = get_user_model().objects.filter(email__exact=email).first()
            refresh = self.get_token(user)
            user_serializer = UserSerializer(user)
            response = {
                "refresh": str(refresh), 'access': str(refresh.access_token),
                "user_detail": user_serializer.data, "message": "Email is verified."}
            return Response(response, status=status.HTTP_200_OK)
        return Response({"response": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)


class ResendSignupUserEmailViewSet(ListCreateAPIView):
    serializer_class = ResendUserSignupEmailSerializer
    queryset = UserSignupCode.objects.none()

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        user_email = EmailAddress.objects.filter(email__exact=email).first()
        if user_email:
            if not user_email.verified:
                code = get_random_str(6)
                while UserSignupCode.objects.filter(code=code).first():
                    code = get_random_str(6)
                instance = UserSignupCode.objects.filter(email=email).first()
                if instance:
                    instance.code = code
                    instance.save()
                message = ""

                html_message = render_to_string("account/email/confirmation.html", {
                    "code": code})
                send_mail(
                    "Tella confirmation code",
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False
                )
                return Response({"response": "Confirmation email sent."})
            return Response({"response": "User already verified."})
        return Response({"response": "Email does not exist."})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
