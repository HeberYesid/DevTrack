import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from accounts.utils import (
    send_verification_code_email,
    verify_turnstile_token,
    send_teacher_invitation_email
)
from accounts.models import EmailVerificationCode, TeacherInvitationCode

User = get_user_model()


@pytest.mark.django_db
class TestSendVerificationCodeEmail:
    """Tests for send_verification_code_email utility function"""
    
    def test_send_verification_code_creates_code(self, student_user):
        """Test that sending verification email creates a code"""
        code = send_verification_code_email(student_user)
        
        assert code is not None
        assert len(code) == 6
        assert code.isdigit()
        
        # Verify code was saved in database
        verification_code = EmailVerificationCode.objects.filter(
            user=student_user, 
            code=code
        ).first()
        assert verification_code is not None
        assert not verification_code.is_used
    
    def test_send_verification_code_sends_email(self, student_user):
        """Test that email is sent"""
        send_verification_code_email(student_user)
        
        assert len(mail.outbox) == 1
        assert student_user.email in mail.outbox[0].to
        assert 'verificación' in mail.outbox[0].subject.lower()
    
    def test_send_password_reset_code(self, student_user):
        """Test sending password reset code"""
        code = send_verification_code_email(student_user, is_password_reset=True)
        
        assert code is not None
        assert len(mail.outbox) == 1
        assert 'contraseña' in mail.outbox[0].subject.lower()
    
    def test_invalidates_previous_codes(self, student_user):
        """Test that previous codes are invalidated"""
        # Create first code
        first_code = send_verification_code_email(student_user)
        
        # Create second code
        second_code = send_verification_code_email(student_user)
        
        # First code should be invalidated
        first_verification = EmailVerificationCode.objects.get(
            user=student_user,
            code=first_code
        )
        assert first_verification.is_used
        
        # Second code should be valid
        second_verification = EmailVerificationCode.objects.get(
            user=student_user,
            code=second_code
        )
        assert not second_verification.is_used


@pytest.mark.django_db
class TestVerifyTurnstileToken:
    """Tests for verify_turnstile_token utility function"""
    
    def test_verify_turnstile_empty_token(self):
        """Test with empty token"""
        assert verify_turnstile_token('') is False
        assert verify_turnstile_token(None) is False
    
    @patch('accounts.utils.settings.DEBUG', True)
    @patch('accounts.utils.os.getenv')
    def test_verify_turnstile_no_secret_in_debug(self, mock_getenv):
        """Test that verification passes in debug mode without secret"""
        mock_getenv.return_value = None
        result = verify_turnstile_token('test_token')
        assert result is True
    
    @patch('accounts.utils.settings.DEBUG', False)
    @patch('accounts.utils.os.getenv')
    def test_verify_turnstile_no_secret_in_production(self, mock_getenv):
        """Test that verification fails in production without secret"""
        mock_getenv.return_value = None
        result = verify_turnstile_token('test_token')
        assert result is False
    
    @patch('accounts.utils.requests.post')
    @patch('accounts.utils.os.getenv')
    def test_verify_turnstile_success(self, mock_getenv, mock_post):
        """Test successful token verification"""
        mock_getenv.return_value = 'test_secret'
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        result = verify_turnstile_token('valid_token', '127.0.0.1')
        assert result is True
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['data']['response'] == 'valid_token'
        assert call_args[1]['data']['remoteip'] == '127.0.0.1'
    
    @patch('accounts.utils.requests.post')
    @patch('accounts.utils.os.getenv')
    def test_verify_turnstile_failure(self, mock_getenv, mock_post):
        """Test failed token verification"""
        mock_getenv.return_value = 'test_secret'
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': False}
        mock_post.return_value = mock_response
        
        result = verify_turnstile_token('invalid_token')
        assert result is False
    
    @patch('accounts.utils.requests.post')
    @patch('accounts.utils.os.getenv')
    def test_verify_turnstile_network_error(self, mock_getenv, mock_post):
        """Test network error during verification"""
        import requests
        mock_getenv.return_value = 'test_secret'
        mock_post.side_effect = requests.RequestException('Network error')
        
        result = verify_turnstile_token('token')
        assert result is False


@pytest.mark.django_db
class TestSendTeacherInvitationEmail:
    """Tests for send_teacher_invitation_email utility function"""
    
    def test_send_invitation_email(self, admin_user):
        """Test sending teacher invitation email"""
        invitation = TeacherInvitationCode.objects.create(
            email='newteacher@example.com',
            code='TESTCODE123',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        send_teacher_invitation_email(invitation)
        
        assert len(mail.outbox) == 1
        assert 'newteacher@example.com' in mail.outbox[0].to
        assert 'invitación' in mail.outbox[0].subject.lower()
        assert 'TESTCODE123' in mail.outbox[0].body
    
    def test_invitation_email_contains_code(self, admin_user):
        """Test that invitation email contains the code"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@test.com',
            code='ABC123XYZ',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        send_teacher_invitation_email(invitation)
        
        email_body = mail.outbox[0].body
        assert 'ABC123XYZ' in email_body
        assert 'register-teacher' in email_body
