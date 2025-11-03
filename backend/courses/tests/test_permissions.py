import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

from courses.models import Subject, Enrollment
from courses.permissions import (
    IsTeacherOrAdmin,
    IsOwnerTeacherOrAdmin,
    IsStudent,
    IsTeacher
)

User = get_user_model()


@pytest.mark.django_db
class TestIsTeacherOrAdmin:
    """Tests for IsTeacherOrAdmin permission"""
    
    def test_teacher_has_permission(self, teacher_user):
        """Test that teachers have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = teacher_user
        
        permission = IsTeacherOrAdmin()
        assert permission.has_permission(request, None) is True
    
    def test_admin_has_permission(self, admin_user):
        """Test that admins have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        
        permission = IsTeacherOrAdmin()
        assert permission.has_permission(request, None) is True
    
    def test_student_no_permission(self, student_user):
        """Test that students don't have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = student_user
        
        permission = IsTeacherOrAdmin()
        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsOwnerTeacherOrAdmin:
    """Tests for IsOwnerTeacherOrAdmin permission"""
    
    def test_owner_teacher_has_permission(self, teacher_user):
        """Test that the owner teacher has permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = teacher_user
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        permission = IsOwnerTeacherOrAdmin()
        assert permission.has_object_permission(request, None, subject) is True
    
    def test_other_teacher_no_permission(self, teacher_user, create_user):
        """Test that other teachers don't have permission"""
        other_teacher = create_user(
            email='other@teacher.com',
            username='other@teacher.com',
            role=User.Roles.TEACHER
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = other_teacher
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        permission = IsOwnerTeacherOrAdmin()
        assert permission.has_object_permission(request, None, subject) is False
    
    def test_admin_has_permission(self, teacher_user, admin_user):
        """Test that admins have permission to any subject"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        permission = IsOwnerTeacherOrAdmin()
        assert permission.has_object_permission(request, None, subject) is True
    
    def test_student_no_permission(self, teacher_user, student_user):
        """Test that students don't have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = student_user
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        permission = IsOwnerTeacherOrAdmin()
        assert permission.has_object_permission(request, None, subject) is False


@pytest.mark.django_db
class TestIsStudent:
    """Tests for IsStudent permission"""
    
    def test_student_has_permission(self, student_user):
        """Test that students have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = student_user
        
        permission = IsStudent()
        assert permission.has_permission(request, None) is True
    
    def test_teacher_no_permission(self, teacher_user):
        """Test that teachers don't have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = teacher_user
        
        permission = IsStudent()
        assert permission.has_permission(request, None) is False
    
    def test_admin_no_permission(self, admin_user):
        """Test that admins don't have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        
        permission = IsStudent()
        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsTeacher:
    """Tests for IsTeacher permission"""
    
    def test_teacher_has_permission(self, teacher_user):
        """Test that teachers have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = teacher_user
        
        permission = IsTeacher()
        assert permission.has_permission(request, None) is True
    
    def test_student_no_permission(self, student_user):
        """Test that students don't have permission"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = student_user
        
        permission = IsTeacher()
        assert permission.has_permission(request, None) is False
    
    def test_admin_no_permission(self, admin_user):
        """Test that admins don't have permission (only teachers)"""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        
        permission = IsTeacher()
        # Note: Admins are not teachers, so they shouldn't have this permission
        # unless the permission is changed to include admins
        assert permission.has_permission(request, None) is False
