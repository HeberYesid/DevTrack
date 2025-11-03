"""
Comprehensive tests for accounts serializers.
Phase 3: Serializer validation testing.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from unittest.mock import patch, MagicMock

from accounts.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    VerifyCodeSerializer,
    ResendCodeSerializer,
    RegisterTeacherSerializer,
)
from accounts.models import EmailVerificationCode, TeacherInvitationCode

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer"""
    
    def test_serialize_user(self, student_user):
        """Test serializing a user"""
        serializer = UserSerializer(student_user)
        data = serializer.data
        
        assert data['email'] == student_user.email
        assert data['username'] == student_user.username
        assert data['role'] == student_user.role
        assert 'password' not in data
        assert 'is_verified' in data
    
    def test_is_verified_field(self, create_user):
        """Test is_verified field maps to is_email_verified"""
        user = create_user(email='test@test.com', username='test@test.com')
        user.is_email_verified = True
        user.save()
        
        serializer = UserSerializer(user)
        assert serializer.data['is_verified'] is True
        assert serializer.data['is_email_verified'] is True


@pytest.mark.django_db
class TestRegisterSerializer:
    """Test RegisterSerializer validation and creation"""
    
    @patch('accounts.serializers.verify_turnstile_token')
    @patch('accounts.serializers.send_verification_code_email')
    def test_create_user_success(self, mock_send_email, mock_verify_turnstile):
        """Test successful user registration"""
        mock_verify_turnstile.return_value = True
        mock_send_email.return_value = None
        
        data = {
            'email': 'newuser@test.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Roles.STUDENT,
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        
        assert user.email == 'newuser@test.com'
        assert user.username == 'newuser@test.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.role == User.Roles.STUDENT
        assert user.is_active is True
        assert user.is_email_verified is False
        assert user.check_password('securepass123')
        
        mock_verify_turnstile.assert_called_once()
        mock_send_email.assert_called_once_with(user)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_create_user_invalid_turnstile(self, mock_verify_turnstile):
        """Test registration fails with invalid turnstile token"""
        mock_verify_turnstile.return_value = False
        
        data = {
            'email': 'test@test.com',
            'password': 'password123',
            'turnstile_token': 'invalid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterSerializer(data=data, context={'request': request})
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Verificación de seguridad fallida' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_password_min_length(self, mock_verify_turnstile):
        """Test password must be at least 8 characters"""
        mock_verify_turnstile.return_value = True
        
        data = {
            'email': 'test@test.com',
            'password': 'short',  # Less than 8 characters
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_email_normalization(self, mock_verify_turnstile):
        """Test email is normalized to lowercase"""
        mock_verify_turnstile.return_value = True
        
        data = {
            'email': 'TeSt@TeSt.CoM',
            'password': 'password123',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        with patch('accounts.serializers.send_verification_code_email'):
            user = serializer.save()
        
        assert user.email == 'test@test.com'
        assert user.username == 'test@test.com'
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_default_role_is_student(self, mock_verify_turnstile):
        """Test default role is STUDENT"""
        mock_verify_turnstile.return_value = True
        
        data = {
            'email': 'test@test.com',
            'password': 'password123',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
        
        with patch('accounts.serializers.send_verification_code_email'):
            user = serializer.save()
        
        assert user.role == User.Roles.STUDENT


@pytest.mark.django_db
class TestLoginSerializer:
    """Test LoginSerializer validation"""
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_login_success(self, mock_verify_turnstile, create_user):
        """Test successful login"""
        mock_verify_turnstile.return_value = True
        
        user = create_user(
            email='user@test.com',
            username='user@test.com',
            password='password123'
        )
        user.is_email_verified = True
        user.save()
        
        data = {
            'email': 'user@test.com',
            'password': 'password123',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = LoginSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        validated_data = serializer.validated_data
        assert 'access' in validated_data
        assert 'refresh' in validated_data
        assert 'user' in validated_data
        assert validated_data['user']['email'] == 'user@test.com'
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_login_invalid_turnstile(self, mock_verify_turnstile):
        """Test login fails with invalid turnstile"""
        mock_verify_turnstile.return_value = False
        
        data = {
            'email': 'user@test.com',
            'password': 'password123',
            'turnstile_token': 'invalid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = LoginSerializer(data=data, context={'request': request})
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Verificación de seguridad fallida' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_login_user_not_found(self, mock_verify_turnstile):
        """Test login fails when user doesn't exist"""
        mock_verify_turnstile.return_value = True
        
        data = {
            'email': 'nonexistent@test.com',
            'password': 'password123',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = LoginSerializer(data=data, context={'request': request})
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Credenciales inválidas' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_login_wrong_password(self, mock_verify_turnstile, create_user):
        """Test login fails with wrong password"""
        mock_verify_turnstile.return_value = True
        
        create_user(
            email='user@test.com',
            username='user@test.com',
            password='correct_password'
        )
        
        data = {
            'email': 'user@test.com',
            'password': 'wrong_password',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = LoginSerializer(data=data, context={'request': request})
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Credenciales inválidas' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_login_email_not_verified(self, mock_verify_turnstile, create_user):
        """Test login fails when email is not verified"""
        mock_verify_turnstile.return_value = True
        
        user = create_user(
            email='user@test.com',
            username='user@test.com',
            password='password123'
        )
        user.is_email_verified = False
        user.save()
        
        data = {
            'email': 'user@test.com',
            'password': 'password123',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = LoginSerializer(data=data, context={'request': request})
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'verificar tu correo' in str(exc_info.value)


@pytest.mark.django_db
class TestVerifyCodeSerializer:
    """Test VerifyCodeSerializer"""
    
    def test_verify_code_success(self, create_user):
        """Test successful code verification"""
        user = create_user(email='user@test.com', username='user@test.com')
        code = user.create_email_verification_code(minutes_valid=15)
        
        data = {
            'email': 'user@test.com',
            'code': code
        }
        
        serializer = VerifyCodeSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        validated_data = serializer.validated_data
        assert validated_data['user'] == user
        assert validated_data['verification_code'].code == code
    
    def test_verify_code_user_not_found(self):
        """Test verification fails when user doesn't exist"""
        data = {
            'email': 'nonexistent@test.com',
            'code': '123456'
        }
        
        serializer = VerifyCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Usuario no encontrado' in str(exc_info.value)
    
    def test_verify_code_invalid_code(self, create_user):
        """Test verification fails with invalid code"""
        user = create_user(email='user@test.com', username='user@test.com')
        user.create_email_verification_code(minutes_valid=15)
        
        data = {
            'email': 'user@test.com',
            'code': '999999'  # Wrong code
        }
        
        serializer = VerifyCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Código inválido' in str(exc_info.value)
    
    def test_verify_code_already_used(self, create_user):
        """Test verification fails when code is already used"""
        user = create_user(email='user@test.com', username='user@test.com')
        code = user.create_email_verification_code(minutes_valid=15)
        
        # Mark code as used
        verification = EmailVerificationCode.objects.get(user=user, code=code)
        verification.is_used = True
        verification.save()
        
        data = {
            'email': 'user@test.com',
            'code': code
        }
        
        serializer = VerifyCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Código inválido' in str(exc_info.value)
    
    def test_verify_code_expired(self, create_user):
        """Test verification fails when code is expired"""
        user = create_user(email='user@test.com', username='user@test.com')
        code = user.create_email_verification_code(minutes_valid=-1)  # Already expired
        
        data = {
            'email': 'user@test.com',
            'code': code
        }
        
        serializer = VerifyCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Código expirado' in str(exc_info.value)


@pytest.mark.django_db
class TestResendCodeSerializer:
    """Test ResendCodeSerializer"""
    
    def test_resend_code_valid_email(self, create_user):
        """Test resending code to unverified user"""
        user = create_user(email='user@test.com', username='user@test.com')
        user.is_email_verified = False
        user.save()
        
        data = {'email': 'user@test.com'}
        
        serializer = ResendCodeSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['email'] == 'user@test.com'
    
    def test_resend_code_already_verified(self, create_user):
        """Test resending fails when user is already verified"""
        user = create_user(email='user@test.com', username='user@test.com')
        user.is_email_verified = True
        user.save()
        
        data = {'email': 'user@test.com'}
        
        serializer = ResendCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'ya está verificada' in str(exc_info.value)
    
    def test_resend_code_user_not_found(self):
        """Test resending fails when user doesn't exist"""
        data = {'email': 'nonexistent@test.com'}
        
        serializer = ResendCodeSerializer(data=data)
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'Usuario no encontrado' in str(exc_info.value)


@pytest.mark.django_db
class TestRegisterTeacherSerializer:
    """Test RegisterTeacherSerializer"""
    
    @patch('accounts.serializers.verify_turnstile_token')
    @patch('accounts.serializers.send_verification_code_email')
    def test_register_teacher_success(self, mock_send_email, mock_verify_turnstile, admin_user):
        """Test successful teacher registration with valid invitation"""
        from django.utils import timezone
        from datetime import timedelta
        
        mock_verify_turnstile.return_value = True
        mock_send_email.return_value = None
        
        # Create invitation code
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@test.com',
            created_by=admin_user,
            code=TeacherInvitationCode.generate_code(),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        data = {
            'email': 'teacher@test.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'Teacher',
            'invitation_code': invitation.code,
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterTeacherSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        
        assert user.email == 'teacher@test.com'
        assert user.role == User.Roles.TEACHER
        assert user.is_email_verified is False
        
        # Verify invitation is marked as used
        invitation.refresh_from_db()
        assert invitation.used is True
        assert invitation.used_by == user
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_register_teacher_invalid_code(self, mock_verify_turnstile, admin_user):
        """Test teacher registration fails with invalid invitation code"""
        mock_verify_turnstile.return_value = True
        
        data = {
            'email': 'teacher@test.com',
            'password': 'securepass123',
            'invitation_code': 'INVALID_CODE',
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterTeacherSerializer(data=data, context={'request': request})
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'inválido' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_register_teacher_already_used_code(self, mock_verify_turnstile, admin_user, create_user):
        """Test teacher registration fails when code is already used"""
        from django.utils import timezone
        from datetime import timedelta
        
        mock_verify_turnstile.return_value = True
        
        other_user = create_user(email='other@test.com', username='other@test.com')
        
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@test.com',
            created_by=admin_user,
            code=TeacherInvitationCode.generate_code(),
            expires_at=timezone.now() + timedelta(days=7)
        )
        invitation.mark_used(other_user)
        
        data = {
            'email': 'teacher@test.com',
            'password': 'securepass123',
            'invitation_code': invitation.code,
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterTeacherSerializer(data=data, context={'request': request})
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'ya ha sido utilizado' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_register_teacher_expired_code(self, mock_verify_turnstile, admin_user):
        """Test teacher registration fails when code is expired"""
        from django.utils import timezone
        from datetime import timedelta
        
        mock_verify_turnstile.return_value = True
        
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@test.com',
            created_by=admin_user,
            code=TeacherInvitationCode.generate_code(),
            expires_at=timezone.now() - timedelta(days=1)  # Already expired
        )
        
        data = {
            'email': 'teacher@test.com',
            'password': 'securepass123',
            'invitation_code': invitation.code,
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterTeacherSerializer(data=data, context={'request': request})
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'expirado' in str(exc_info.value)
    
    @patch('accounts.serializers.verify_turnstile_token')
    def test_register_teacher_email_mismatch(self, mock_verify_turnstile, admin_user):
        """Test teacher registration fails when email doesn't match invitation"""
        from django.utils import timezone
        from datetime import timedelta
        
        mock_verify_turnstile.return_value = True
        
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@test.com',
            created_by=admin_user,
            code=TeacherInvitationCode.generate_code(),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        data = {
            'email': 'different@test.com',  # Different email
            'password': 'securepass123',
            'invitation_code': invitation.code,
            'turnstile_token': 'valid_token'
        }
        
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        serializer = RegisterTeacherSerializer(data=data, context={'request': request})
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'no corresponde' in str(exc_info.value)
