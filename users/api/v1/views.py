from django.contrib.auth import get_user_model
from django_rest_passwordreset.models import get_password_reset_token_expiry_time, ResetPasswordToken
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_rest_passwordreset.models import get_password_reset_token_expiry_time
from django_rest_passwordreset.serializers import EmailSerializer
from django_rest_passwordreset.views import ResetPasswordConfirmViewSet, ResetPasswordValidateTokenViewSet, ResetPasswordRequestTokenViewSet
from rest_framework import serializers


class CustomPasswordValidateMixin:
    def validate(self, data):
        token = data.get('token')

        # get token validation time
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # find token
        try:
            reset_password_token = _get_object_or_404(ResetPasswordToken, key=token)
        except (TypeError, ValueError, ValidationError, Http404,
                ResetPasswordToken.DoesNotExist):
            raise serializers.ValidationError(_("The OTP password entered is not valid. Please check and try again."))

        # check expiry date
        expiry_date = reset_password_token.created_at + timedelta(
            hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            # delete expired token
            reset_password_token.delete()
            raise serializers.ValidationError(_("The token has expired"))
        return data


class CustomPasswordTokenSerializer(CustomPasswordValidateMixin, serializers.Serializer):
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})
    token = serializers.CharField()


class CustomResetTokenSerializer(CustomPasswordValidateMixin, serializers.Serializer):
    token = serializers.CharField()


class CustomEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomResetPasswordRequestTokenViewSet(ResetPasswordRequestTokenViewSet):
    serializer_class = CustomEmailSerializer

    def create(self, request, *args, **kwargs):
        return super(ResetPasswordRequestTokenViewSet, self).post(request, *args, **kwargs)


class CustomResetPasswordValidateTokenViewSet(ResetPasswordValidateTokenViewSet):
    serializer_class = CustomResetTokenSerializer

    def create(self, request, *args, **kwargs):
        return super(ResetPasswordValidateTokenViewSet, self).post(request, *args, **kwargs)


class CustomResetPasswordConfirmViewSet(ResetPasswordConfirmViewSet):
    serializer_class = CustomPasswordTokenSerializer

    def create(self, request, *args, **kwargs):
        return super(ResetPasswordConfirmViewSet, self).post(request, *args, **kwargs)

