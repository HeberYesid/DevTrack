import pytest
from django.urls import reverse
from courses.models import Subject, Enrollment, Exercise, StudentExerciseResult


@pytest.mark.django_db
class TestSubjectAPI:
    """Tests for Subject API endpoints"""
    
    def test_list_subjects_as_student(self, authenticated_client, teacher_user, student_user):
        """Test listing subjects as student"""
        s1 = Subject.objects.create(name='Math', code='MATH101', teacher=teacher_user)
        s2 = Subject.objects.create(name='Physics', code='PHY101', teacher=teacher_user)
        
        # Enroll student in both
        Enrollment.objects.create(student=student_user, subject=s1)
        Enrollment.objects.create(student=student_user, subject=s2)
        
        url = reverse('subject-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 2
    
    def test_list_subjects_unauthenticated(self, api_client, teacher_user):
        """Test listing subjects without authentication"""
        Subject.objects.create(name='Math', code='MATH101', teacher=teacher_user)
        
        url = reverse('subject-list')
        response = api_client.get(url)
        
        assert response.status_code == 401
    
    def test_create_subject_as_teacher(self, teacher_client):
        """Test creating subject as teacher"""
        url = reverse('subject-list')
        data = {
            'name': 'Chemistry',
            'code': 'CHEM101',
            'description': 'Basic Chemistry'
        }
        response = teacher_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Subject.objects.filter(code='CHEM101').exists()
    
    def test_get_subject_detail(self, authenticated_client, teacher_user):
        """Test getting subject detail"""
        subject = Subject.objects.create(
            name='Biology',
            code='BIO101',
            teacher=teacher_user
        )
        
        authenticated_client.force_authenticate(user=teacher_user)
        url = reverse('subject-detail', kwargs={'pk': subject.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['name'] == 'Biology'


@pytest.mark.django_db
class TestEnrollmentAPI:
    """Tests for Enrollment API endpoints"""
    
    def test_enroll_in_subject(self, authenticated_client, student_user, teacher_user):
        """Test enrolling in a subject (by Teacher)"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        
        # Authenticate as teacher because only teachers can enroll
        authenticated_client.force_authenticate(user=teacher_user)
        
        url = reverse('subject-enrollments', args=[subject.id])
        data = {'student_email': student_user.email}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Enrollment.objects.filter(
            student=student_user,
            subject=subject
        ).exists()
    
    def test_list_my_enrollments(self, authenticated_client, student_user, teacher_user):
        """Test listing student's enrollments"""
        subject1 = Subject.objects.create(name='Math', code='MATH101', teacher=teacher_user)
        subject2 = Subject.objects.create(name='Physics', code='PHY101', teacher=teacher_user)
        
        Enrollment.objects.create(student=student_user, subject=subject1)
        Enrollment.objects.create(student=student_user, subject=subject2)
        
        # Authenticate as student
        authenticated_client.force_authenticate(user=student_user)
        
        url = reverse('my-enrollments')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data['enrollments']) == 2
    
    def test_cannot_enroll_twice(self, authenticated_client, student_user, teacher_user):
        """Test that student cannot be enrolled twice in same subject"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        Enrollment.objects.create(student=student_user, subject=subject)
        
        # Authenticate as teacher
        authenticated_client.force_authenticate(user=teacher_user)
        
        url = reverse('subject-enrollments', args=[subject.id])
        data = {'student_email': student_user.email}
        
        response = authenticated_client.post(url, data, format='json')
        # Expect 400 because student already enrolled
        assert response.status_code == 400


@pytest.mark.django_db
class TestExerciseAPI:
    """Tests for Exercise API endpoints"""
    
    def test_list_exercises_for_subject(self, authenticated_client, student_user, teacher_user):
        """Test listing exercises for a subject"""
        subject = Subject.objects.create(
            name='Math',
            code='MATH101',
            teacher=teacher_user
        )
        exercise1 = Exercise.objects.create(
            subject=subject,
            name='Exercise 1',
            order=1
        )
        exercise2 = Exercise.objects.create(
            subject=subject,
            name='Exercise 2',
            order=2
        )
        
        assert Exercise.objects.filter(subject=subject).count() == 2
        assert exercise1.name == 'Exercise 1'
        assert exercise2.order == 2


@pytest.mark.django_db
class TestStudentExerciseResultAPI:
    """Tests for StudentExerciseResult API endpoints"""
    
    def test_create_result(self, authenticated_client, student_user, teacher_user):
        """Test creating an exercise result"""
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
        
        assert result.status == StudentExerciseResult.Status.GREEN
        assert result.enrollment == enrollment
    
    def test_list_results_for_enrollment(self, authenticated_client, student_user, teacher_user):
        """Test listing results for an enrollment"""
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
        StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=StudentExerciseResult.Status.YELLOW
        )
        
        results = StudentExerciseResult.objects.filter(enrollment=enrollment)
        assert results.count() == 1
        assert results.first().status == StudentExerciseResult.Status.YELLOW
