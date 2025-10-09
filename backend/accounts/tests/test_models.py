import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import EmailVerificationCode, TeacherInvitationCode

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model"""
    
    def test_create_user(self, user_data):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username=user_data['email'],
            email=user_data['email'],
            password=user_data['password']
        )
        assert user.email == user_data['email']
        assert user.username == user_data['email']
        assert user.check_password(user_data['password'])
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active
    
    def test_user_roles(self, create_user):
        """Test user role assignment"""
        student = create_user(role=User.Roles.STUDENT)
        teacher = create_user(
            email='teacher@test.com',
            username='teacher@test.com',
            role=User.Roles.TEACHER
        )
        
        assert student.role == User.Roles.STUDENT
        assert teacher.role == User.Roles.TEACHER
    
    def test_user_str_representation(self, student_user):
        """Test string representation of user"""
        assert str(student_user) == student_user.email


@pytest.mark.django_db
class TestEmailVerificationCode:
    """Tests for EmailVerificationCode model"""
    
    def test_create_verification_code(self, student_user):
        """Test creating a verification code"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        assert code.user == student_user
        assert code.code == '123456'
        assert not code.used
    
    def test_verification_code_is_valid(self, student_user):
        """Test if verification code is valid"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        assert code.is_valid()
    
    def test_verification_code_expired(self, student_user):
        """Test expired verification code"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        assert not code.is_valid()
    
    def test_verification_code_used(self, student_user):
        """Test used verification code"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15),
            used=True
        )
        assert not code.is_valid()
    
    def test_mark_code_as_used(self, student_user):
        """Test marking code as used"""
        code = EmailVerificationCode.objects.create(
            user=student_user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        code.mark_used()
        assert code.used


@pytest.mark.django_db
class TestTeacherInvitationCode:
    """Tests for TeacherInvitationCode model"""
    
    def test_create_invitation_code(self, admin_user):
        """Test creating an invitation code"""
        invitation = TeacherInvitationCode.objects.create(
            email='newteacher@example.com',
            code='ABC123DEF456',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        assert invitation.email == 'newteacher@example.com'
        assert invitation.code == 'ABC123DEF456'
        assert not invitation.used
    
    def test_generate_code(self):
        """Test code generation"""
        code = TeacherInvitationCode.generate_code()
        assert len(code) == 12
        assert code.isupper()
    
    def test_invitation_is_valid(self, admin_user):
        """Test if invitation is valid"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        assert invitation.is_valid()
    
    def test_invitation_expired(self, admin_user):
        """Test expired invitation"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        assert not invitation.is_valid()
    
    def test_invitation_already_used(self, admin_user):
        """Test already used invitation"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7),
            used=True
        )
        assert not invitation.is_valid()
    
    def test_mark_invitation_as_used(self, admin_user, teacher_user):
        """Test marking invitation as used"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invitation.mark_used(teacher_user)
        
        assert invitation.used
        assert invitation.used_by == teacher_user
        assert invitation.used_at is not None
    
    def test_invitation_str_representation(self, admin_user):
        """Test string representation of invitation"""
        invitation = TeacherInvitationCode.objects.create(
            email='teacher@example.com',
            code='TEST12345678',
            created_by=admin_user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        assert 'teacher@example.com' in str(invitation)
        assert 'TEST12345678' in str(invitation)
        assert 'Disponible' in str(invitation)
