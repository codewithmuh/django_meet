from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.api.v1.viewsets import (
    SignupViewSet,
    VerifyUserSignupCodeViewSet,
    ResendSignupUserEmailViewSet,
    CustomTokenObtainPairView
)

router = DefaultRouter()
router.register("signup", SignupViewSet, basename="signup")

urlpatterns = [
    path("", include(router.urls)),
    path('jwt-login/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', TokenRefreshView.as_view()),
    path('jwt/verify/', TokenVerifyView.as_view()),
    path('verify-email/', VerifyUserSignupCodeViewSet.as_view(), name='verify_email_code'),
    path('resend-email/', ResendSignupUserEmailViewSet.as_view(), name='resend-email'),
    path('forgot-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
