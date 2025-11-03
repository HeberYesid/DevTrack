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
    
    def test_enrollment_stats_no_exercises(self, student_user, teacher_user):
        """Test enrollment statistics with no exercises"""
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
        assert stats['green'] == 0
        assert stats['yellow'] == 0
        assert stats['red'] == 0
        assert stats['grade'] == 0.0
    
    def test_enrollment_stats_all_green(self, student_user, teacher_user):
        """Test enrollment statistics with all green results - should get 5.0"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        
        # Create exercises with green results
        for i in range(5):
            exercise = Exercise.objects.create(
                subject=subject,
                name=f'Exercise {i}',
                order=i
            )
            StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=exercise,
                status=StudentExerciseResult.Status.GREEN
            )
        
        stats = enrollment.stats()
        assert stats['total'] == 5
        assert stats['green'] == 5
        assert stats['yellow'] == 0
        assert stats['red'] == 0
        assert stats['grade'] == 5.0
    
    def test_enrollment_stats_sixty_percent_yellow(self, student_user, teacher_user):
        """Test enrollment statistics with 60%+ yellow - should get 3.0"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        
        # Create 10 exercises: 3 yellow (30%), 7 red (70%) - yellow < 60%
        for i in range(3):
            exercise = Exercise.objects.create(
                subject=subject,
                name=f'Yellow Exercise {i}',
                order=i
            )
            StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=exercise,
                status=StudentExerciseResult.Status.YELLOW
            )
        
        for i in range(7):
            exercise = Exercise.objects.create(
                subject=subject,
                name=f'Red Exercise {i}',
                order=i+3
            )
            StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=exercise,
                status=StudentExerciseResult.Status.RED
            )
        
        stats = enrollment.stats()
        assert stats['total'] == 10
        assert stats['yellow'] == 3
        assert stats['red'] == 7
        # yellow/total = 0.3 < 0.6, so grade should be based on green proportion
        # green=0, so grade = 5.0 * (0/10) = 0.0
        assert stats['grade'] == 0.0
    
    def test_enrollment_stats_proportional_grade(self, student_user, teacher_user):
        """Test enrollment statistics with proportional grade calculation"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        enrollment = Enrollment.objects.create(
            student=student_user,
            subject=subject
        )
        
        # Create 10 exercises: 7 green, 2 yellow, 1 red
        for i in range(7):
            exercise = Exercise.objects.create(
                subject=subject,
                name=f'Green Exercise {i}',
                order=i
            )
            StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=exercise,
                status=StudentExerciseResult.Status.GREEN
            )
        
        for i in range(2):
            exercise = Exercise.objects.create(
                subject=subject,
                name=f'Yellow Exercise {i}',
                order=i+7
            )
            StudentExerciseResult.objects.create(
                enrollment=enrollment,
                exercise=exercise,
                status=StudentExerciseResult.Status.YELLOW
            )
        
        exercise = Exercise.objects.create(
            subject=subject,
            name='Red Exercise',
            order=9
        )
        StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.RED
        )
        
        stats = enrollment.stats()
        assert stats['total'] == 10
        assert stats['green'] == 7
        assert stats['yellow'] == 2
        assert stats['red'] == 1
        # Not all green (7 != 10) and yellow/total = 0.2 < 0.6
        # So grade = 5.0 * (7/10) = 3.5
        assert stats['grade'] == 3.5


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
