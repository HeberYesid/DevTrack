import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import EmailVerificationCode, TeacherInvitationCode
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
class TestRegistrationAPI:
    """Tests for user registration"""
    
    @patch('accounts.serializers.send_verification_code_email')
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_student_success(self, mock_turnstile, mock_email, api_client):
        """Test successful student registration"""
        url = reverse('register')
        data = {
            'email': 'newstudent@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Student',
            'role': 'STUDENT',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert User.objects.filter(email='newstudent@example.com').exists()
        user = User.objects.get(email='newstudent@example.com')
        assert user.role == User.Roles.STUDENT
        assert not user.is_email_verified
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=False)
    def test_register_without_captcha(self, mock_turnstile, api_client):
        """Test registration without captcha fails"""
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'turnstile_token': 'invalid_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
    
    @patch('accounts.serializers.send_verification_code_email')
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_duplicate_email(self, mock_turnstile, mock_email, api_client, student_user):
        """Test registration with duplicate email"""
        url = reverse('register')
        data = {
            'email': student_user.email,
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginAPI:
    """Tests for user login"""
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_login_success(self, mock_turnstile, api_client, student_user):
        """Test successful login"""
        url = reverse('login')
        data = {
            'email': student_user.email,
            'password': 'testpass123',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_login_invalid_credentials(self, mock_turnstile, api_client, student_user):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            'email': student_user.email,
            'password': 'wrongpassword',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 401
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_login_unverified_email(self, mock_turnstile, api_client, create_user):
        """Test login with unverified email"""
        user = create_user(email='unverified@example.com', username='unverified@example.com')
        user.is_email_verified = False
        user.save()
        
        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'testpass123',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestEmailVerificationAPI:
    """Tests for email verification"""
    
    def test_verify_code_success(self, api_client, student_user):
        """Test successful email verification"""
        student_user.is_email_verified = False
        student_user.save()
        
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        url = reverse('verify-code')
        data = {
            'email': student_user.email,
            'code': '123456'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        student_user.refresh_from_db()
        assert student_user.is_email_verified
        code.refresh_from_db()
        assert code.is_used
    
    def test_verify_invalid_code(self, api_client, student_user):
        """Test verification with invalid code"""
        url = reverse('verify-code')
        data = {
            'email': student_user.email,
            'code': '999999'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
    
    def test_verify_expired_code(self, api_client, student_user):
        """Test verification with expired code"""
        EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        url = reverse('verify-code')
        data = {
            'email': student_user.email,
            'code': '123456'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
    
    def test_resend_code_success(self, api_client, create_user):
        """Test resending verification code"""
        user = create_user(email='resend@example.com', username='resend@example.com')
        user.is_email_verified = False
        user.save()
        
        url = reverse('resend-code')
        data = {'email': user.email}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert EmailVerificationCode.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestTeacherRegistrationAPI:
    """Tests for teacher registration with invitation code"""
    
    @patch('accounts.serializers.send_verification_code_email')
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_teacher_success(self, mock_turnstile, mock_email, api_client, admin_user):
        """Test successful teacher registration"""
        invitation = TeacherInvitationCode.objects.create(
            email='newteacher@example.com',
            code='ABC123DEF456',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        url = reverse('register-teacher')
        data = {
            'email': 'newteacher@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Teacher',
            'invitation_code': 'ABC123DEF456',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert User.objects.filter(email='newteacher@example.com').exists()
        user = User.objects.get(email='newteacher@example.com')
        assert user.role == User.Roles.TEACHER
        
        invitation.refresh_from_db()
        assert invitation.used
        assert invitation.used_by == user
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_teacher_invalid_code(self, mock_turnstile, api_client):
        """Test teacher registration with invalid code"""
        url = reverse('register-teacher')
        data = {
            'email': 'teacher@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'invitation_code': 'INVALID123',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_teacher_expired_code(self, mock_turnstile, api_client, admin_user):
        """Test teacher registration with expired code"""
        TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='EXPIRED12345',
            created_by=admin_user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        url = reverse('register-teacher')
        data = {
            'email': 'teacher@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'invitation_code': 'EXPIRED12345',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400
    
    @patch('accounts.serializers.verify_turnstile_token', return_value=True)
    def test_register_teacher_wrong_email(self, mock_turnstile, api_client, admin_user):
        """Test teacher registration with wrong email"""
        TeacherInvitationCode.objects.create(
            email='correct@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        url = reverse('register-teacher')
        data = {
            'email': 'wrong@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'invitation_code': 'TEST12345678',
            'turnstile_token': 'fake_token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestMeAPI:
    """Tests for current user endpoint"""
    
    def test_get_current_user(self, authenticated_client, student_user):
        """Test getting current user info"""
        url = reverse('me')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['email'] == student_user.email
        assert response.data['role'] == student_user.role
    
    def test_get_current_user_unauthorized(self, api_client):
        """Test getting current user without authentication"""
        url = reverse('me')
        response = api_client.get(url)
        assert response.status_code == 401
