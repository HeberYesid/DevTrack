from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets
import random


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

    def create_email_verification_code(self, minutes_valid: int = 15) -> str:
        """
        Crea un código de verificación de 6 dígitos para el usuario.
        Invalida cualquier código anterior no usado.
        """
        # Invalidar códigos anteriores no usados
        EmailVerificationCode.objects.filter(user=self, used=False).update(used=True)
        
        # Generar nuevo código de 6 dígitos
        code = f"{random.randint(100000, 999999)}"
        expiry = timezone.now() + timedelta(minutes=minutes_valid)
        
        EmailVerificationCode.objects.create(user=self, code=code, expires_at=expiry)
        return code


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


class EmailVerificationCode(models.Model):
    """
    Modelo para códigos de verificación de 6 dígitos enviados por email
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self) -> bool:
        return (not self.used) and timezone.now() < self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=['used'])

    def __str__(self):
        return f"Código {self.code} para {self.user.email}"
