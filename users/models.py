import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    email = models.EmailField(unique=True)
    passport_no = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    gender = models.CharField(choices=(
        ("male", "Male"),
        ("female", "Female"),
        ("x", "X"),
        ("transgender", "Transgender"),
        ("non-binary", "Non-Binary"),
        ("other", "Other")), max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to="profile/", default="default_profile.png", null=True, blank=True)
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email}"


class UserSignupCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = "User Signup Code"


class ApiKey(models.Model):
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.api_key)

    class Meta:
        verbose_name_plural = 'API Allowed Keys'
        ordering = ('-created',)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # send an e-mail to the user
    context = {
        'username': reset_password_token.user.get_full_name,
        'reset_password_token': reset_password_token.key
    }
    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
    msg = EmailMultiAlternatives(
        # title:
        "Password Reset FOR {title}".format(title="Medas insurance"),
        # message:
        email_plaintext_message,
        # from:
        settings.DEFAULT_FROM_EMAIL,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
