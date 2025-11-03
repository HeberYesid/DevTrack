import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status

from accounts.models import EmailVerificationCode


@pytest.mark.django_db
class TestForgotPasswordAPI:
    """Tests for password recovery endpoints"""
    
    def test_forgot_password_existing_user(self, api_client, student_user):
        """Test forgot password with existing user"""
        url = reverse('forgot-password')
        data = {
            'email': student_user.email,
            'turnstile_token': 'test_token'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        # Code should be created
        assert EmailVerificationCode.objects.filter(
            user=student_user,
            code_type='PASSWORD_RESET'
        ).exists()
    
    def test_forgot_password_nonexistent_user(self, api_client):
        """Test forgot password with non-existent user - should still return 200"""
        url = reverse('forgot-password')
        data = {
            'email': 'nonexistent@example.com',
            'turnstile_token': 'test_token'
        }
        response = api_client.post(url, data, format='json')
        
        # Should return 200 to prevent user enumeration
        assert response.status_code == 200
    
    def test_forgot_password_without_turnstile(self, api_client, student_user):
        """Test forgot password without turnstile token"""
        url = reverse('forgot-password')
        data = {
            'email': student_user.email
        }
        response = api_client.post(url, data, format='json')
        
        # Should fail validation
        assert response.status_code == 400


@pytest.mark.django_db
class TestResetPasswordAPI:
    """Tests for password reset endpoint"""
    
    def test_reset_password_success(self, api_client, student_user):
        """Test successful password reset"""
        # Create verification code
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            code_type='PASSWORD_RESET',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        url = reverse('reset-password')
        data = {
            'email': student_user.email,
            'code': '123456',
            'new_password': 'NewSecurePassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        
        # Code should be marked as used
        code.refresh_from_db()
        assert code.is_used
        
        # User should be able to login with new password
        student_user.refresh_from_db()
        assert student_user.check_password('NewSecurePassword123!')
    
    def test_reset_password_invalid_code(self, api_client, student_user):
        """Test password reset with invalid code"""
        url = reverse('reset-password')
        data = {
            'email': student_user.email,
            'code': '999999',
            'new_password': 'NewPassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
    
    def test_reset_password_expired_code(self, api_client, student_user):
        """Test password reset with expired code"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            code_type='PASSWORD_RESET',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        url = reverse('reset-password')
        data = {
            'email': student_user.email,
            'code': '123456',
            'new_password': 'NewPassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
    
    def test_reset_password_weak_password(self, api_client, student_user):
        """Test password reset with weak password"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            code_type='PASSWORD_RESET',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        url = reverse('reset-password')
        data = {
            'email': student_user.email,
            'code': '123456',
            'new_password': '123'  # Too short
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestChangePasswordAPI:
    """Tests for authenticated password change endpoint"""
    
    def test_change_password_success(self, authenticated_client, student_user):
        """Test successful password change"""
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePassword123!'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == 200
        
        # Verify new password works
        student_user.refresh_from_db()
        assert student_user.check_password('NewSecurePassword123!')
    
    def test_change_password_wrong_old_password(self, authenticated_client, student_user):
        """Test password change with wrong old password"""
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewPassword123!'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == 400
    
    def test_change_password_unauthenticated(self, api_client):
        """Test password change when not authenticated"""
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewPassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 401
    
    def test_change_password_weak_new_password(self, authenticated_client, student_user):
        """Test password change with weak new password"""
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'weak'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestUserExistsAPI:
    """Tests for user exists check endpoint"""
    
    def test_user_exists(self, api_client, student_user):
        """Test checking if user exists"""
        url = reverse('user-exists')
        response = api_client.get(url, {'email': student_user.email})
        
        assert response.status_code == 200
        assert response.data['exists'] is True
    
    def test_user_not_exists(self, api_client):
        """Test checking if non-existent user exists"""
        url = reverse('user-exists')
        response = api_client.get(url, {'email': 'nonexistent@example.com'})
        
        assert response.status_code == 200
        assert response.data['exists'] is False
    
    def test_user_exists_no_email(self, api_client):
        """Test user exists endpoint without email parameter"""
        url = reverse('user-exists')
        response = api_client.get(url)
        
        assert response.status_code == 400
