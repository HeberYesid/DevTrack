import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """API client for testing"""
    return APIClient()


@pytest.fixture
def user_data():
    """Sample user data"""
    return {
        'email': 'test@example.com',
        'username': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def create_user(db, user_data):
    """Factory to create a user"""
    def make_user(**kwargs):
        data = user_data.copy()
        data.update(kwargs)
        password = data.pop('password')
        user = User.objects.create(**data)
        user.set_password(password)
        user.is_email_verified = True
        user.save()
        return user
    return make_user


@pytest.fixture
def student_user(create_user):
    """Create a student user"""
    return create_user(
        email='student@example.com',
        username='student@example.com',
        role=User.Roles.STUDENT
    )


@pytest.fixture
def teacher_user(create_user):
    """Create a teacher user"""
    return create_user(
        email='teacher@example.com',
        username='teacher@example.com',
        role=User.Roles.TEACHER
    )


@pytest.fixture
def admin_user(create_user):
    """Create an admin user"""
    return create_user(
        email='admin@example.com',
        username='admin@example.com',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def authenticated_client(api_client, student_user):
    """API client with authenticated student"""
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def teacher_client(api_client, teacher_user):
    """API client with authenticated teacher"""
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client with authenticated admin"""
    api_client.force_authenticate(user=admin_user)
    return api_client
