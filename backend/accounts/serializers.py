from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import send_verification_email, send_verification_code_email, verify_turnstile_token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(source='is_email_verified', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified', 'is_verified', 'is_active', 'session_timeout']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Roles.choices, default=User.Roles.STUDENT)
    turnstile_token = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'turnstile_token']

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        turnstile_token = attrs.get('turnstile_token')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Este email ya está registrado.'})
        
        # Get client IP from request context
        request = self.context.get('request')
        remote_ip = None
        if request:
            remote_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if remote_ip:
                remote_ip = remote_ip.split(',')[0].strip()
            else:
                remote_ip = request.META.get('REMOTE_ADDR')
        
        print(f"🔍 Validando Turnstile - Token: {turnstile_token[:20]}... | IP: {remote_ip}")
        
        if not verify_turnstile_token(turnstile_token, remote_ip):
            print(f"❌ Turnstile falló para {email}")
            raise serializers.ValidationError({'turnstile_token': 'Verificación de seguridad fallida. Intenta de nuevo.'})
        
        print(f"✅ Turnstile validado correctamente para {email}")
        return attrs

    def create(self, validated_data):
        # Remove turnstile_token from validated_data as it's not a model field
        validated_data.pop('turnstile_token', None)
        
        email = validated_data['email'].lower().strip()
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        role = validated_data.get('role', User.Roles.STUDENT)

        # Use email as username for simplicity
        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)
        user.is_active = True
        user.is_email_verified = False
        user.save()

        # Send verification code email
        send_verification_code_email(user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    turnstile_token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')
        turnstile_token = attrs.get('turnstile_token')
        
        # Verify Turnstile token first
        request = self.context.get('request')
        remote_ip = None
        if request:
            remote_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if remote_ip:
                remote_ip = remote_ip.split(',')[0].strip()
            else:
                remote_ip = request.META.get('REMOTE_ADDR')
        
        if not verify_turnstile_token(turnstile_token, remote_ip):
            raise AuthenticationFailed('Verificación de seguridad fallida. Intenta de nuevo.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Credenciales inválidas.')

        if not user.check_password(password):
            raise AuthenticationFailed('Credenciales inválidas.')

        if not user.is_email_verified:
            raise AuthenticationFailed('Debes verificar tu correo con el código de 6 dígitos para iniciar sesión.')

        refresh = RefreshToken.for_user(user)
        data: dict[str, Any] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }
        return data


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        code = attrs.get('code', '').strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado.')

        # Buscar el código más reciente no usado
        from .models import EmailVerificationCode
        verification_code = EmailVerificationCode.objects.filter(
            user=user, 
            code=code, 
            is_used=False
        ).first()

        if not verification_code:
            raise serializers.ValidationError('Código inválido.')

        if not verification_code.is_valid():
            raise serializers.ValidationError('Código expirado.')

        attrs['user'] = user
        attrs['verification_code'] = verification_code
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.lower().strip()
        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                raise serializers.ValidationError('Esta cuenta ya está verificada.')
            return email
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado.')


class RegisterTeacherSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    invitation_code = serializers.CharField(write_only=True, required=True)
    turnstile_token = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'invitation_code', 'turnstile_token']

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        invitation_code = attrs.get('invitation_code', '').strip()
        turnstile_token = attrs.get('turnstile_token')
        
        # Verify Turnstile token
        request = self.context.get('request')
        remote_ip = None
        if request:
            remote_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if remote_ip:
                remote_ip = remote_ip.split(',')[0].strip()
            else:
                remote_ip = request.META.get('REMOTE_ADDR')
        
        if not verify_turnstile_token(turnstile_token, remote_ip):
            raise serializers.ValidationError('Verificación de seguridad fallida. Intenta de nuevo.')
        
        # Verificar código de invitación
        from .models import TeacherInvitationCode
        try:
            invitation = TeacherInvitationCode.objects.get(code=invitation_code)
        except TeacherInvitationCode.DoesNotExist:
            raise serializers.ValidationError({'invitation_code': 'Código de invitación inválido.'})
        
        if invitation.used:
            raise serializers.ValidationError({'invitation_code': 'Este código ya ha sido utilizado.'})
        
        if not invitation.is_valid():
            raise serializers.ValidationError({'invitation_code': 'Este código ha expirado.'})
        
        # Verificar que el email coincida con el de la invitación
        if invitation.email.lower() != email:
            raise serializers.ValidationError({'email': 'Este email no corresponde al código de invitación.'})
        
        attrs['invitation'] = invitation
        return attrs

    def create(self, validated_data):
        # Remove non-model fields
        invitation = validated_data.pop('invitation')
        validated_data.pop('invitation_code', None)
        validated_data.pop('turnstile_token', None)
        
        email = validated_data['email'].lower().strip()
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        # Create teacher user
        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=User.Roles.TEACHER,  # Forzar rol de profesor
        )
        user.set_password(password)
        user.is_active = True
        user.is_email_verified = False
        user.save()

        # Mark invitation as used
        invitation.mark_used(user)

        # Send verification code email
        send_verification_code_email(user)
        return user


class ContactMessageSerializer(serializers.Serializer):
    """
    Serializer para mensajes de contacto del formulario público
    """
    name = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.ChoiceField(
        choices=['soporte', 'registro', 'calificaciones', 'profesor', 'bug', 'sugerencia', 'otro'],
        required=True
    )
    message = serializers.CharField(required=True, min_length=10)
    
    def validate_email(self, value):
        """Validar formato de email"""
        return value.lower().strip()
    
    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value.strip()
    
    def validate_message(self, value):
        """Validar longitud del mensaje"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe tener al menos 10 caracteres")
        return value.strip()

