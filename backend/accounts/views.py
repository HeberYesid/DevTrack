from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth import get_user_model

from .models import EmailVerificationToken, EmailVerificationCode
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer, 
    VerifyCodeSerializer, 
    ResendCodeSerializer,
    RegisterTeacherSerializer
)
from .utils import send_verification_code_email

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'Registro exitoso. Hemos enviado un código de verificación de 6 dígitos a tu correo.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

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


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

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


class ResendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

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


class RegisterTeacherView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterTeacherSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registro de profesor exitoso. Hemos enviado un código de verificación de 6 dígitos a tu correo.'
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    """View para obtener y actualizar el perfil del usuario autenticado"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Obtener perfil del usuario"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Actualizar perfil del usuario"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Solo permitir actualizar first_name y last_name
        allowed_fields = ['first_name', 'last_name']
        for field in request.data.keys():
            if field not in allowed_fields:
                return Response(
                    {'detail': f'No se permite actualizar el campo: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer.save()
        return Response(serializer.data)


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

        return Response(
            {'message': 'Contraseña cambiada exitosamente'}, 
            status=status.HTTP_200_OK
        )
