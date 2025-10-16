from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    LoginView, 
    VerifyEmailView, 
    VerifyCodeView, 
    ResendCodeView, 
    MeView,
    RegisterTeacherView,
    ProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
    CheckUserExistsView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-teacher/', RegisterTeacherView.as_view(), name='register-teacher'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('check-user-exists/', CheckUserExistsView.as_view(), name='check-user-exists'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
