from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        TEACHER = 'TEACHER', 'Profesor'
        STUDENT = 'STUDENT', 'Estudiante'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    is_email_verified = models.BooleanField(default=False)

    def create_email_verification_token(self, hours_valid: int = 48) -> str:
        token = secrets.token_urlsafe(48)
        expiry = timezone.now() + timedelta(hours=hours_valid)
        EmailVerificationToken.objects.create(user=self, token=token, expires_at=expiry)
        return token


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        return (not self.used) and timezone.now() < self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=['used'])
