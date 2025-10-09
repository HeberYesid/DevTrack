import pytest
from django.contrib.auth import get_user_model
from courses.models import Subject, Enrollment, Exercise, StudentExerciseResult

User = get_user_model()


@pytest.mark.django_db
class TestSubjectModel:
    """Tests for Subject model"""
    
    def test_create_subject(self, teacher_user):
        """Test creating a subject"""
        subject = Subject.objects.create(
            name='Mathematics',
            code='MATH101',
            teacher=teacher_user
        )
        assert subject.name == 'Mathematics'
        assert subject.code == 'MATH101'
        assert subject.teacher == teacher_user
    
    def test_subject_str_representation(self, teacher_user):
        """Test string representation of subject"""
        subject = Subject.objects.create(
            name='Physics',
            code='PHY101',
            teacher=teacher_user
        )
        assert str(subject) == 'PHY101 - Physics'


@pytest.mark.django_db
class TestEnrollmentModel:
    """Tests for Enrollment model"""
    
    def test_create_enrollment(self, student_user, teacher_user):
        """Test creating an enrollment"""
        subject = Subject.objects.create(
            name='Chemistry',
            code='CHEM101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        assert enrollment.student == student_user
        assert enrollment.subject == subject
        assert enrollment.created_at is not None
    
    def test_enrollment_str_representation(self, student_user, teacher_user):
        """Test string representation of enrollment"""
        subject = Subject.objects.create(
            name='Biology',
            code='BIO101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        assert student_user.email in str(enrollment)
        assert 'BIO101' in str(enrollment)
    
    def test_enrollment_stats(self, student_user, teacher_user):
        """Test enrollment statistics calculation"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        
        stats = enrollment.stats()
        assert stats['total'] == 0
        assert stats['grade'] == 0.0


@pytest.mark.django_db
class TestExerciseModel:
    """Tests for Exercise model"""
    
    def test_create_exercise(self, teacher_user):
        """Test creating an exercise"""
        subject = Subject.objects.create(
            name='History',
            code='HIST101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Ancient Rome Essay',
            order=1
        )
        assert exercise.name == 'Ancient Rome Essay'
        assert exercise.subject == subject
        assert exercise.order == 1
    
    def test_exercise_str_representation(self, teacher_user):
        """Test string representation of exercise"""
        subject = Subject.objects.create(
            name='Literature',
            code='LIT101',
            teacher=teacher_user
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Poetry Analysis',
            order=1
        )
        assert 'Poetry Analysis' in str(exercise)
        assert 'LIT101' in str(exercise)


@pytest.mark.django_db
class TestStudentExerciseResultModel:
    """Tests for StudentExerciseResult model"""
    
    def test_create_result(self, student_user, teacher_user):
        """Test creating an exercise result"""
        subject = Subject.objects.create(
            name='Computer Science',
            code='CS101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Programming Task',
            order=1
        )
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        assert result.enrollment == enrollment
        assert result.exercise == exercise
        assert result.status == StudentExerciseResult.Status.GREEN
    
    def test_result_statuses(self, student_user, teacher_user):
        """Test different result statuses"""
        subject = Subject.objects.create(
            name='Art',
            code='ART101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Drawing',
            order=1
        )
        
        for status in [StudentExerciseResult.Status.GREEN, 
                      StudentExerciseResult.Status.YELLOW, 
                      StudentExerciseResult.Status.RED]:
            result = StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=Exercise.objects.create(
                    subject=subject,
                    name=f'Task {status}',
                    order=len(StudentExerciseResult.Status.choices)
                ),
                status=status
            )
            assert result.status == status
    
    def test_result_str_representation(self, student_user, teacher_user):
        """Test string representation of result"""
        subject = Subject.objects.create(
            name='Music',
            code='MUS101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        exercise = Exercise.objects.create(
            subject=subject,
            name='Compose a Song',
            order=1
        )
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.GREEN
        )
        assert 'Compose a Song' in str(result)
        assert student_user.email in str(result)
        assert 'GREEN' in str(result)
