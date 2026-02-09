from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.views import TokenRefreshView
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer

from django.contrib.auth import get_user_model
from datetime import timedelta
import random

from .models import EmailVerificationToken, EmailVerificationCode, ContactMessage, TeacherInvitationCode
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer, 
    VerifyCodeSerializer, 
    ResendCodeSerializer,
    RegisterTeacherSerializer,
    ContactMessageSerializer,
    GoogleLoginSerializer
)
from .utils import send_verification_code_email
from .ratelimit import ratelimit_auth, ratelimit_strict_auth, ratelimit_email

User = get_user_model()


@method_decorator(ratelimit_auth, name='post')
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register new user",
        description="Register a new user and send verification code.",
        request=RegisterSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'Registro exitoso. Hemos enviado un código de verificación de 6 dígitos a tu correo.'}, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit_auth, name='post')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Login",
        description="Login with email and password to get JWT tokens.",
        request=LoginSerializer,
        responses={200: LoginSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Verify email with token",
        parameters=[
            OpenApiParameter(
                name="token",
                description="Verification token",
                required=True,
                type=str,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        token_value = request.query_params.get('token')
        if not token_value:
            return Response({'detail': 'Token no provisto.'}, status=status.HTTP_400_BAD_REQUEST)

        evt = get_object_or_404(EmailVerificationToken, token=token_value)
        if not evt.is_valid():
            return Response({'detail': 'Token inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        user = evt.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        evt.mark_used()

        return Response({'message': 'Correo verificado exitosamente. Ya puedes iniciar sesión.'}, status=status.HTTP_200_OK)


@method_decorator(ratelimit_strict_auth, name='post')
class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Verify email with 6-digit code",
        request=VerifyCodeSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        verification_code = serializer.validated_data['verification_code']
        
        # Marcar el código como usado
        verification_code.mark_used()
        
        # Verificar el email del usuario
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        
        print(f"✅ Usuario {user.email} verificado exitosamente con código {verification_code.code}")
        
        return Response({
            'message': 'Correo verificado exitosamente. Ya puedes iniciar sesión.'
        }, status=status.HTTP_200_OK)


@method_decorator(ratelimit_email, name='post')
class ResendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Resend verification code",
        request=ResendCodeSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Enviar nuevo código
        send_verification_code_email(user)
        
        return Response({
            'message': 'Nuevo código de verificación enviado a tu correo.'
        }, status=status.HTTP_200_OK)


@method_decorator(ratelimit_auth, name='post')
class RegisterTeacherView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register new teacher",
        request=RegisterTeacherSerializer,
        responses={201: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = RegisterTeacherSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registro de profesor exitoso. Hemos enviado un código de verificación de 6 dígitos a tu correo.'
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get current user",
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    """View para obtener y actualizar el perfil del usuario autenticado"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get profile",
        responses={200: UserSerializer},
    )
    def get(self, request):
        """Obtener perfil del usuario"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update profile",
        request=UserSerializer,
        responses={200: UserSerializer},
    )
    def patch(self, request):
        """Actualizar perfil del usuario"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Solo permitir actualizar first_name, last_name y session_timeout
        allowed_fields = ['first_name', 'last_name', 'session_timeout']
        for field in request.data.keys():
            if field not in allowed_fields:
                return Response(
                    {'detail': f'No se permite actualizar el campo: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar session_timeout si se proporciona
        if 'session_timeout' in request.data:
            timeout = request.data['session_timeout']
            if not isinstance(timeout, int) or timeout < 5 or timeout > 120:
                return Response(
                    {'session_timeout': ['El timeout debe ser un número entre 5 y 120 minutos']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer.save()
        return Response(serializer.data)


@method_decorator(ratelimit_strict_auth, name='post')
class ChangePasswordView(APIView):
    """View para cambiar la contraseña del usuario autenticado"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'detail': 'Se requieren current_password y new_password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar contraseña actual
        if not user.check_password(current_password):
            return Response(
                {'current_password': ['La contraseña actual es incorrecta']}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar nueva contraseña
        if len(new_password) < 8:
            return Response(
                {'new_password': ['La contraseña debe tener al menos 8 caracteres']}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cambiar contraseña
        user.set_password(new_password)
        user.save()

        # Crear notificación de seguridad
        from courses.models import Notification
        from django.utils import timezone
        
        Notification.objects.create(
            user=user,
            notification_type='GENERAL',
            title=' Contraseña actualizada',
            message=f'Tu contraseña fue cambiada exitosamente el {timezone.now().strftime("%d/%m/%Y a las %H:%M")}. Si no fuiste tú, contacta al administrador inmediatamente.',
            is_read=False
        )

        return Response(
            {'message': 'Contraseña cambiada exitosamente'}, 
            status=status.HTTP_200_OK
        )


@method_decorator(ratelimit_email, name='post')
class ForgotPasswordView(APIView):
    """Envía un código de verificación para recuperar contraseña"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response(
                {'detail': 'El email es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            return Response(
                {'message': 'Si el email existe, recibirás un código de verificación'}, 
                status=status.HTTP_200_OK
            )
        
        # Enviar email con código de verificación
        send_verification_code_email(user, is_password_reset=True)
        
        return Response(
            {'message': 'Si el email existe, recibirás un código de verificación'}, 
            status=status.HTTP_200_OK
        )


@method_decorator(ratelimit_strict_auth, name='post')
class ResetPasswordView(APIView):
    """Restablece la contraseña usando el código de verificación"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '')
        
        if not all([email, code, new_password]):
            return Response(
                {'detail': 'Email, código y nueva contraseña son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar longitud de contraseña
        if len(new_password) < 8:
            return Response(
                {'detail': 'La contraseña debe tener al menos 8 caracteres'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Código inválido o expirado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar código válido
        try:
            verification_code = EmailVerificationCode.objects.get(
                user=user,
                code=code,
                code_type='PASSWORD_RESET',
                is_used=False
            )
            
            if not verification_code.is_valid():
                return Response(
                    {'detail': 'El código ha expirado. Solicita uno nuevo'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except EmailVerificationCode.DoesNotExist:
            return Response(
                {'detail': 'Código inválido o expirado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Marcar código como usado
        verification_code.mark_used()
        
        # Crear notificación de seguridad
        from courses.models import Notification
        
        Notification.objects.create(
            user=user,
            notification_type='GENERAL',
            title='🔐 Contraseña restablecida',
            message=f'Tu contraseña fue restablecida exitosamente el {timezone.now().strftime("%d/%m/%Y a las %H:%M")}. Si no fuiste tú, contacta al administrador inmediatamente.',
            is_read=False
        )
        
        return Response(
            {'message': 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión'}, 
            status=status.HTTP_200_OK
        )


class CheckUserExistsView(APIView):
    """
    Vista para verificar si un usuario existe en la plataforma por email.
    Útil para profesores que quieren saber si un estudiante ya tiene cuenta.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Check if user exists",
        parameters=[
            OpenApiParameter(name="email", type=str, required=True),
        ],
        responses={
            200: inline_serializer(
                name="UserExistsResponse",
                fields={
                    "exists": serializers.BooleanField(),
                    "email": serializers.EmailField(),
                    "first_name": serializers.CharField(),
                    "last_name": serializers.CharField(),
                    "role": serializers.CharField(),
                    "is_active": serializers.BooleanField(),
                    "is_verified": serializers.BooleanField(),
                },
            )
        },
    )
    def get(self, request):
        """
        Verifica si existe un usuario con el email proporcionado.
        Retorna información básica del usuario si existe.
        """
        email = request.query_params.get('email', '').strip().lower()
        
        if not email:
            return Response(
                {'detail': 'El parámetro email es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Retornar información básica del usuario
            return Response({
                'exists': True,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': getattr(user, 'role', 'STUDENT'),
                'is_active': user.is_active,
                'is_verified': user.is_verified if hasattr(user, 'is_verified') else True
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'exists': False, 'detail': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ContactMessageView(APIView):
    """
    Vista para recibir mensajes del formulario de contacto público.
    No requiere autenticación pero sí verificación de Turnstile.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Send contact message",
        request=ContactMessageSerializer,
        responses={201: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        """Crear un nuevo mensaje de contacto"""
        serializer = ContactMessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar Turnstile
        turnstile_token = serializer.validated_data.get('turnstile_token')
        
        # Obtener IP del cliente
        remote_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if remote_ip:
            remote_ip = remote_ip.split(',')[0].strip()
        else:
            remote_ip = request.META.get('REMOTE_ADDR')
        
        from .utils import verify_turnstile_token
        if not verify_turnstile_token(turnstile_token, remote_ip):
            return Response(
                {'error': 'Verificación de seguridad fallida. Por favor intenta de nuevo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar el mensaje en la base de datos
        contact_message = ContactMessage.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message']
        )
        
        # TODO: Opcionalmente enviar email de notificación al admin
        # send_contact_notification_email(contact_message)
        
        return Response(
            {
                'message': 'Mensaje enviado exitosamente. Te responderemos pronto.',
                'id': contact_message.id
            },
            status=status.HTTP_201_CREATED
        )


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Google Login",
        request=GoogleLoginSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['id_token']

        try:
            client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
            print(f"🔍 Verifying Google Token. Client ID: {client_id}")
            
            # Specify the CLIENT_ID of the app that accesses the backend:
            # Added clock_skew_in_seconds to handle local dev time differences
            id_info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                client_id,
                clock_skew_in_seconds=300
            )

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            email = id_info['email'].lower()
            first_name = id_info.get('given_name', '')
            last_name = id_info.get('family_name', '')

            user = User.objects.filter(email=email).first()

            if not user:
                # Registration logic
                role = serializer.validated_data.get('role', User.Roles.STUDENT)
                invitation_code = serializer.validated_data.get('invitation_code')
                
                if role == User.Roles.TEACHER:
                    if not invitation_code:
                         return Response({'error': 'Se requiere código de invitación para registrarse como profesor.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    try:
                        invitation = TeacherInvitationCode.objects.get(code=invitation_code)
                        if invitation.used:
                             return Response({'error': 'Este código de invitación ya ha sido utilizado.'}, status=status.HTTP_400_BAD_REQUEST)
                        if not invitation.is_valid():
                             return Response({'error': 'Este código de invitación ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)
                        if invitation.email.lower() != email:
                             return Response({'error': 'Este email no corresponde al código de invitación.'}, status=status.HTTP_400_BAD_REQUEST)
                             
                        # Valid invitation
                        user = User.objects.create(
                            username=email,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            role=User.Roles.TEACHER,
                            is_email_verified=True
                        )
                        user.set_unusable_password()
                        user.save()
                        
                        invitation.mark_used(user)
                        
                    except TeacherInvitationCode.DoesNotExist:
                        return Response({'error': 'Código de invitación inválido.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Student registration
                    user = User.objects.create(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Roles.STUDENT,
                        is_email_verified=True
                    )
                    user.set_unusable_password()
                    user.save()
            
            # If user exists but wasn't verified, verify them now
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()

            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        except ValueError as e:
            # Invalid token
            print(f"❌ Google Token Verification Failed: {str(e)}")
            return Response({'error': f'Token de Google inválido: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ Google Login Error: {str(e)}")
            return Response({'error': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
