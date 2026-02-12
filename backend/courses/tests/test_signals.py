import pytest
from django.contrib.auth import get_user_model

from courses.models import Subject, Enrollment, Exercise, StudentExerciseResult
from notifications.models import Notification

User = get_user_model()


@pytest.mark.django_db
class TestEnrollmentSignals:
    """Tests for enrollment-related signals"""
    
    def test_enrollment_creates_notifications(self, student_user, teacher_user):
        """Test that creating enrollment creates notifications for both student and teacher"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        # Clear any existing notifications
        Notification.objects.all().delete()
        
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        
        # Should create 2 notifications: one for student, one for teacher
        notifications = Notification.objects.all()
        assert notifications.count() == 2
        
        student_notif = Notification.objects.filter(recipient=student_user).first()
        assert student_notif is not None
        assert 'inscrito' in student_notif.title.lower() or 'enrollment' in student_notif.title.lower()
        
        teacher_notif = Notification.objects.filter(recipient=teacher_user).first()
        assert teacher_notif is not None


@pytest.mark.django_db
class TestResultSignals:
    """Tests for student result-related signals"""
    
    def test_result_create_notification(self, student_user, teacher_user):
        """Test that creating a result creates notification"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Exercise 1',
            order=1
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        
        # Should create notification
        notifications = Notification.objects.filter(recipient=student_user)
        assert notifications.count() > 0
    
    def test_result_update_notification(self, student_user, teacher_user):
        """Test that updating a result creates notification"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Exercise 1',
            order=1
        )
        
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.YELLOW
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        # Update result
        result.status = StudentExerciseResult.Status.GREEN
        result.save()
        
        # Should create notification
        notifications = Notification.objects.filter(recipient=student_user)
        assert notifications.count() > 0


@pytest.mark.django_db
class TestSubjectSignals:
    """Tests for subject-related signals"""
    
    def test_subject_delete_cascades(self, student_user, teacher_user):
        """Test that deleting subject deletes related enrollments and results"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Exercise 1',
            order=1
        )
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        
        result_id = result.id
        enrollment_id = enrollment.id
        
        # Delete subject
        subject.delete()
        
        # Enrollment and result should be deleted
        assert not Enrollment.objects.filter(id=enrollment_id).exists()
        assert not StudentExerciseResult.objects.filter(id=result_id).exists()
