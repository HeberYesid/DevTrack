"""
Tests for rate limiting functionality.

These tests verify that rate limiting is properly applied to authentication
endpoints to protect against brute force attacks.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.core.cache import cache
from accounts.models import User


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test to ensure clean state"""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestRateLimitLogin:
    """Test rate limiting on login endpoint"""
    
    def test_login_allows_5_attempts(self, api_client):
        """Test that 5 login attempts are allowed within the rate limit"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'turnstile_token': 'test-token'
        }
        
        # First 5 attempts should not be rate limited
        # They may fail authentication, but should not return 429
        for i in range(5):
            response = api_client.post(url, data, format='json')
            # Should be 400 or 401 (auth failure), NOT 429 (rate limit)
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED
            ], f"Attempt {i+1} should not be rate limited"
    
    def test_login_blocks_6th_attempt(self, api_client):
        """Test that the 6th login attempt is blocked by rate limiting"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'turnstile_token': 'test-token'
        }
        
        # Make 5 attempts
        for _ in range(5):
            api_client.post(url, data, format='json')
        
        # 6th attempt should be rate limited
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert 'Demasiados intentos' in response.json()['detail']


@pytest.mark.django_db
class TestRateLimitRegister:
    """Test rate limiting on registration endpoint"""
    
    def test_register_allows_5_attempts(self, api_client):
        """Test that 5 registration attempts are allowed"""
        url = reverse('register')
        
        # First 5 attempts should not be rate limited
        for i in range(5):
            data = {
                'email': f'test{i}@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'turnstile_token': 'test-token'
            }
            response = api_client.post(url, data, format='json')
            # May fail validation, but should not be rate limited
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_register_blocks_6th_attempt(self, api_client):
        """Test that the 6th registration attempt is blocked"""
        url = reverse('register')
        
        # Make 5 attempts
        for i in range(5):
            data = {
                'email': f'test{i}@example.com',
                'password': 'testpass123',
                'turnstile_token': 'test-token'
            }
            api_client.post(url, data, format='json')
        
        # 6th attempt should be rate limited
        data = {
            'email': 'test6@example.com',
            'password': 'testpass123',
            'turnstile_token': 'test-token'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
class TestRateLimitVerifyCode:
    """Test rate limiting on code verification endpoint"""
    
    def test_verify_code_allows_3_attempts(self, api_client):
        """Test that 3 verification attempts are allowed"""
        url = reverse('verify-code')
        
        # First 3 attempts should not be rate limited
        for i in range(3):
            data = {
                'email': 'test@example.com',
                'code': '123456'
            }
            response = api_client.post(url, data, format='json')
            # May fail validation, but should not be rate limited
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_verify_code_blocks_4th_attempt(self, api_client):
        """Test that the 4th verification attempt is blocked"""
        url = reverse('verify-code')
        data = {
            'email': 'test@example.com',
            'code': '123456'
        }
        
        # Make 3 attempts
        for _ in range(3):
            api_client.post(url, data, format='json')
        
        # 4th attempt should be rate limited
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
class TestRateLimitResendCode:
    """Test rate limiting on resend code endpoint"""
    
    def test_resend_code_allows_3_attempts(self, api_client):
        """Test that 3 resend attempts are allowed in 5 minutes"""
        # Create a user first
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('resend-code')
        data = {'email': 'test@example.com'}
        
        # First 3 attempts should not be rate limited
        for i in range(3):
            response = api_client.post(url, data, format='json')
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_resend_code_blocks_4th_attempt(self, api_client):
        """Test that the 4th resend attempt is blocked"""
        # Create a user first
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('resend-code')
        data = {'email': 'test@example.com'}
        
        # Make 3 attempts
        for _ in range(3):
            api_client.post(url, data, format='json')
        
        # 4th attempt should be rate limited
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert 'error' in response.json()
        assert response.json()['error'] == 'rate_limit_exceeded'


@pytest.mark.django_db
class TestRateLimitChangePassword:
    """Test rate limiting on change password endpoint"""
    
    def test_change_password_allows_3_attempts(self, authenticated_client, student_user):
        """Test that 3 password change attempts are allowed"""
        url = reverse('change-password')
        
        # First 3 attempts should not be rate limited
        for i in range(3):
            data = {
                'current_password': 'wrongpass',
                'new_password': 'newpass123'
            }
            response = authenticated_client.post(url, data, format='json')
            # May fail validation, but should not be rate limited
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_change_password_blocks_4th_attempt(self, authenticated_client, student_user):
        """Test that the 4th password change attempt is blocked"""
        url = reverse('change-password')
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123'
        }
        
        # Make 3 attempts
        for _ in range(3):
            authenticated_client.post(url, data, format='json')
        
        # 4th attempt should be rate limited
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
class TestRateLimitResponse:
    """Test the format of rate limit error responses"""
    
    def test_rate_limit_response_format(self, api_client):
        """Test that rate limit responses have correct format"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'turnstile_token': 'test-token'
        }
        
        # Trigger rate limit
        for _ in range(6):
            response = api_client.post(url, data, format='json')
        
        # Check response format
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        response_data = response.json()
        assert 'detail' in response_data
        assert 'error' in response_data
        assert response_data['error'] == 'rate_limit_exceeded'
        assert isinstance(response_data['detail'], str)


# Integration test
@pytest.mark.django_db
class TestRateLimitIntegration:
    """Integration tests for rate limiting across multiple endpoints"""
    
    def test_rate_limits_are_independent_per_endpoint(self, api_client):
        """Test that rate limits are tracked separately for each endpoint"""
        login_url = reverse('login')
        register_url = reverse('register')
        
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'turnstile_token': 'test-token'
        }
        
        register_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'turnstile_token': 'test-token'
        }
        
        # Make 5 login attempts
        for _ in range(5):
            api_client.post(login_url, login_data, format='json')
        
        # Register should still work (independent limit)
        response = api_client.post(register_url, register_data, format='json')
        assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
        
        # But 6th login should be blocked
        response = api_client.post(login_url, login_data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
