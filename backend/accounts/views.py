from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth import get_user_model

from .models import EmailVerificationToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'Registro exitoso. Revisa tu correo para verificar tu cuenta.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
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


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
