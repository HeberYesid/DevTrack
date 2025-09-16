from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import send_verification_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Roles.choices, default=User.Roles.STUDENT)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
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

        # Send verification email
        send_verification_email(user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Credenciales inválidas.')

        if not user.check_password(password):
            raise AuthenticationFailed('Credenciales inválidas.')

        if not user.is_email_verified:
            raise AuthenticationFailed('Debes verificar tu correo para iniciar sesión.')

        refresh = RefreshToken.for_user(user)
        data: dict[str, Any] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }
        return data
