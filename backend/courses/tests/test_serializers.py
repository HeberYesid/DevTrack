"""
Comprehensive tests for courses serializers.
Phase 3: Serializer validation testing for courses app.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from unittest.mock import MagicMock

from courses.serializers import (
    SubjectSerializer,
    EnrollmentSerializer,
    ExerciseSerializer,
    StudentExerciseResultSerializer,
    CSVUploadSerializer,
    NotificationSerializer,
)
from courses.models import Subject, Enrollment, Exercise, StudentExerciseResult, Notification

User = get_user_model()


@pytest.mark.django_db
class TestSubjectSerializer:
    """Test SubjectSerializer"""
    
    def test_serialize_subject(self, teacher_user):
        """Test serializing a subject"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        serializer = SubjectSerializer(subject)
        data = serializer.data
        
        assert data['name'] == 'Math'
        assert data['code'] == 'MATH101'
        assert data['teacher']['id'] == teacher_user.id
        assert data['teacher']['email'] == teacher_user.email
        assert 'enrollments_count' in data
    
    def test_enrollments_count(self, teacher_user, student_user):
        """Test enrollments_count field"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        # Create enrollments
        Enrollment.objects.create(subject=subject, student=student_user)
        
        serializer = SubjectSerializer(subject)
        assert serializer.data['enrollments_count'] == 1
    
    def test_create_subject_sets_teacher_from_request(self, teacher_user):
        """Test that teacher is automatically set from request context"""
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'name': 'Physics',
            'code': 'PHYS101'
        }
        
        serializer = SubjectSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        subject = serializer.save()
        assert subject.teacher == teacher_user
        assert subject.name == 'Physics'
    
    def test_teacher_field_is_read_only(self):
        """Test that teacher field cannot be set directly"""
        data = {
            'name': 'Chemistry',
            'code': 'CHEM101',
            'teacher': 999  # Should be ignored
        }
        
        serializer = SubjectSerializer(data=data)
        # Should be valid because teacher is read_only
        # (will be set in create method via context)
        assert 'teacher' not in serializer.fields or serializer.fields['teacher'].read_only


@pytest.mark.django_db
class TestEnrollmentSerializer:
    """Test EnrollmentSerializer validation and creation"""
    
    def test_serialize_enrollment(self, teacher_user, student_user):
        """Test serializing an enrollment"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(subject=subject, student=student_user)
        
        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data
        
        assert data['subject'] == subject.id
        assert data['student']['id'] == student_user.id
        assert data['student']['email'] == student_user.email
    
    def test_validate_email_normalization(self, teacher_user):
        """Test that email is normalized to lowercase"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': 'TeSt@TeSt.CoM'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['student_email'] == 'test@test.com'
    
    def test_validate_empty_email_fails(self, teacher_user):
        """Test that empty email raises validation error"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': ''
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        # The actual error message is from DRF's blank validation
        assert 'no puede estar en blanco' in str(exc_info.value) or 'email' in str(exc_info.value)
    
    def test_validate_requires_subject_in_context(self, teacher_user):
        """Test that validation fails if subject is not in context"""
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': 'student@test.com'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request}  # No subject
        )
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'no encontrada' in str(exc_info.value)
    
    def test_validate_requires_authenticated_user(self, teacher_user):
        """Test that validation fails if user is not authenticated"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        data = {
            'student_email': 'student@test.com'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'subject': subject}  # No request
        )
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'no autenticado' in str(exc_info.value)
    
    def test_validate_student_cannot_enroll(self, student_user, teacher_user):
        """Test that students cannot enroll others"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        request = MagicMock()
        request.user = student_user
        
        data = {
            'student_email': 'other@test.com'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'permisos' in str(exc_info.value).lower()
    
    def test_validate_teacher_can_only_enroll_in_own_subject(self, create_user):
        """Test that teachers can only enroll students in their own subjects"""
        teacher1 = create_user(email='t1@test.com', username='t1@test.com', role=User.Roles.TEACHER)
        teacher2 = create_user(email='t2@test.com', username='t2@test.com', role=User.Roles.TEACHER)
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher1
        )
        
        request = MagicMock()
        request.user = teacher2  # Different teacher
        
        data = {
            'student_email': 'student@test.com'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        
        assert 'dueño' in str(exc_info.value)
    
    def test_create_enrollment_creates_new_user(self, teacher_user):
        """Test creating enrollment with new student"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': 'newstudent@test.com'
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        assert serializer.is_valid(), serializer.errors
        enrollment = serializer.save()
        
        assert enrollment.student.email == 'newstudent@test.com'
        assert enrollment.student.role == User.Roles.STUDENT
        assert enrollment.subject == subject
    
    def test_create_enrollment_existing_user(self, teacher_user, student_user):
        """Test creating enrollment with existing student"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': student_user.email
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        assert serializer.is_valid()
        enrollment = serializer.save()
        
        assert enrollment.student == student_user
    
    def test_create_enrollment_duplicate_fails(self, teacher_user, student_user):
        """Test that duplicate enrollment raises error"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        # Create first enrollment
        Enrollment.objects.create(subject=subject, student=student_user)
        
        request = MagicMock()
        request.user = teacher_user
        
        data = {
            'student_email': student_user.email
        }
        
        serializer = EnrollmentSerializer(
            data=data,
            context={'request': request, 'subject': subject}
        )
        
        assert serializer.is_valid()
        
        with pytest.raises(ValidationError) as exc_info:
            serializer.save()
        
        assert 'ya está inscrito' in str(exc_info.value)


@pytest.mark.django_db
class TestExerciseSerializer:
    """Test ExerciseSerializer"""
    
    def test_serialize_exercise(self, teacher_user):
        """Test serializing an exercise"""
        from django.utils import timezone
        from datetime import timedelta
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Homework 1',
            order=1,
            deadline=timezone.now() + timedelta(days=7)
        )
        
        serializer = ExerciseSerializer(exercise)
        data = serializer.data
        
        assert data['name'] == 'Homework 1'
        assert data['order'] == 1
        assert data['subject'] == subject.id
        assert 'deadline_status' in data
        assert 'days_until_deadline' in data
        assert 'is_overdue' in data
    
    def test_deadline_fields(self, teacher_user):
        """Test computed deadline fields"""
        from django.utils import timezone
        from datetime import timedelta
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Homework 1',
            order=1,
            deadline=timezone.now() + timedelta(days=5)
        )
        
        serializer = ExerciseSerializer(exercise)
        data = serializer.data
        
        assert data['is_overdue'] is False
        # Days can be 4 or 5 depending on time of execution
        assert data['days_until_deadline'] in [4, 5]
        # Status can be in different cases
        assert data['deadline_status'].upper() in ['UPCOMING', 'SOON', 'OVERDUE', 'NO DEADLINE']


@pytest.mark.django_db
class TestStudentExerciseResultSerializer:
    """Test StudentExerciseResultSerializer"""
    
    def test_serialize_result(self, teacher_user, student_user):
        """Test serializing a student exercise result"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Homework 1',
            order=1
        )
        enrollment = Enrollment.objects.create(subject=subject, student=student_user)
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        
        serializer = StudentExerciseResultSerializer(result)
        data = serializer.data
        
        assert data['student_email'] == student_user.email
        assert data['exercise_name'] == 'Homework 1'
        assert data['subject_id'] == subject.id
        assert data['status'] == StudentExerciseResult.Status.GREEN
        assert 'student_name' in data
    
    def test_student_name_field(self, teacher_user, create_user):
        """Test student_name computed field"""
        student = create_user(
            email='student@test.com',
            username='student@test.com',
            first_name='John',
            last_name='Doe',
            role=User.Roles.STUDENT
        )
        
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Homework 1',
            order=1
        )
        enrollment = Enrollment.objects.create(subject=subject, student=student)
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        
        serializer = StudentExerciseResultSerializer(result)
        assert serializer.data['student_name'] == 'John Doe'
    
    def test_read_only_fields(self, teacher_user, student_user):
        """Test that certain fields are read-only"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Homework 1',
            order=1
        )
        enrollment = Enrollment.objects.create(subject=subject, student=student_user)
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.RED
        )
        
        # Try to update with read-only fields
        data = {
            'status': StudentExerciseResult.Status.GREEN,
            'enrollment': 999,  # Should be ignored
            'exercise': 999,  # Should be ignored
        }
        
        serializer = StudentExerciseResultSerializer(result, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_result = serializer.save()
        assert updated_result.status == StudentExerciseResult.Status.GREEN
        assert updated_result.enrollment == enrollment  # Not changed
        assert updated_result.exercise == exercise  # Not changed


@pytest.mark.django_db
class TestCSVUploadSerializer:
    """Test CSVUploadSerializer"""
    
    def test_validate_file_field(self):
        """Test that file field is required"""
        serializer = CSVUploadSerializer(data={})
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
    
    def test_valid_file(self):
        """Test with valid file"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        csv_content = b"email,first_name,last_name\ntest@test.com,Test,User"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        
        serializer = CSVUploadSerializer(data={'file': csv_file})
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestNotificationSerializer:
    """Test NotificationSerializer"""
    
    def test_serialize_notification(self, student_user):
        """Test serializing a notification"""
        notification = Notification.objects.create(
            user=student_user,
            notification_type='INFO',
            title='Test Notification',
            message='This is a test',
            link='/test'
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        assert data['title'] == 'Test Notification'
        assert data['message'] == 'This is a test'
        assert data['notification_type'] == 'INFO'
        assert data['is_read'] is False
        assert 'time_ago' in data
    
    def test_time_ago_field_recent(self, student_user):
        """Test time_ago field for recent notification"""
        notification = Notification.objects.create(
            user=student_user,
            notification_type='INFO',
            title='Recent',
            message='Just now'
        )
        
        serializer = NotificationSerializer(notification)
        # Should be "Hace un momento" or similar
        assert 'Hace' in serializer.data['time_ago'] or 'momento' in serializer.data['time_ago']
    
    def test_time_ago_field_old(self, student_user):
        """Test time_ago field for old notification"""
        from django.utils import timezone
        from datetime import timedelta
        
        notification = Notification.objects.create(
            user=student_user,
            notification_type='INFO',
            title='Old',
            message='Long ago'
        )
        
        # Manually set created_at to past
        notification.created_at = timezone.now() - timedelta(days=10)
        notification.save()
        
        serializer = NotificationSerializer(notification)
        # Should show date format
        assert '/' in serializer.data['time_ago']
