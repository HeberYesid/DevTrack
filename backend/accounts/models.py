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
    session_timeout = models.IntegerField(
        default=30,
        help_text='Tiempo de inactividad en minutos antes de cerrar sesión automáticamente (5-120 minutos)'
    )

    def create_email_verification_token(self, hours_valid: int = 48) -> str:
        token = secrets.token_urlsafe(48)
        expiry = timezone.now() + timedelta(hours=hours_valid)
        EmailVerificationToken.objects.create(user=self, token=token, expires_at=expiry)
        return token

    def create_email_verification_code(self, minutes_valid: int = 15, code_type: str = 'EMAIL_VERIFICATION') -> str:
        """
        Crea un código de verificación de 6 dígitos para el usuario.
        Invalida cualquier código anterior no usado del mismo tipo.
        """
        # Invalidar códigos anteriores no usados del mismo tipo
        EmailVerificationCode.objects.filter(user=self, is_used=False, code_type=code_type).update(is_used=True)
        
        # Generar nuevo código de 6 dígitos
        code = f"{random.randint(100000, 999999)}"
        expiry = timezone.now() + timedelta(minutes=minutes_valid)
        
        EmailVerificationCode.objects.create(
            user=self, 
            code=code, 
            expires_at=expiry, 
            code_type=code_type
        )
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
    CODE_TYPES = (
        ('EMAIL_VERIFICATION', 'Verificación de Email'),
        ('PASSWORD_RESET', 'Recuperación de Contraseña'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    code_type = models.CharField(max_length=20, choices=CODE_TYPES, default='EMAIL_VERIFICATION')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self) -> bool:
        return (not self.is_used) and timezone.now() < self.expires_at

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    def __str__(self):
        return f"Código {self.code} ({self.get_code_type_display()}) para {self.user.email}"


class TeacherInvitationCode(models.Model):
    """
    Código de invitación para registro de profesores.
    Solo el admin puede crear estos códigos.
    """
    email = models.EmailField(unique=True, help_text="Email del profesor a invitar")
    code = models.CharField(max_length=12, unique=True, help_text="Código de invitación")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invitations')
    expires_at = models.DateTimeField(help_text="Fecha de expiración")
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_invitation')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Código de Invitación de Profesor"
        verbose_name_plural = "Códigos de Invitación de Profesores"

    def is_valid(self) -> bool:
        """Verifica si el código es válido (no usado y no expirado)"""
        return (not self.used) and timezone.now() < self.expires_at

    def mark_used(self, user):
        """Marca el código como usado"""
        self.used = True
        self.used_at = timezone.now()
        self.used_by = user
        self.save(update_fields=['used', 'used_at', 'used_by'])

    @staticmethod
    def generate_code() -> str:
        """Genera un código único de invitación"""
        return secrets.token_urlsafe(9)[:12].upper()

    def __str__(self):
        status = "Usado" if self.used else "Disponible"
        return f"{self.email} - {self.code} ({status})"


class ContactMessage(models.Model):
    """
    Modelo para almacenar mensajes de contacto del formulario público
    """
    SUBJECT_CHOICES = (
        ('soporte', 'Soporte Técnico'),
        ('registro', 'Problema con Registro'),
        ('calificaciones', 'Consulta sobre Calificaciones'),
        ('profesor', 'Solicitud de Acceso como Profesor'),
        ('bug', 'Reportar un Error'),
        ('sugerencia', 'Sugerencia o Mejora'),
        ('otro', 'Otro'),
    )
    
    name = models.CharField(max_length=200, help_text="Nombre completo del remitente")
    email = models.EmailField(help_text="Email de contacto")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, help_text="Asunto del mensaje")
    message = models.TextField(help_text="Contenido del mensaje")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="Marca si el mensaje fue leído")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"

