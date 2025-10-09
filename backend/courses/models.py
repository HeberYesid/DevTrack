from __future__ import annotations
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subject', 'student')
        indexes = [
            models.Index(fields=['subject', 'student']),
        ]
        ordering = ['student__first_name', 'student__last_name', 'student__email']

    def __str__(self) -> str:
        return f"{self.student.email} in {self.subject.code}"

    # Statistics and grade calculation
    def results_qs(self):
        return self.results.select_related('exercise')

    def stats(self) -> dict:
        qs = self.results_qs()
        total = qs.count()
        green = qs.filter(status=StudentExerciseResult.Status.GREEN).count()
        yellow = qs.filter(status=StudentExerciseResult.Status.YELLOW).count()
        red = qs.filter(status=StudentExerciseResult.Status.RED).count()
        grade = 0.0
        semaphore = 'RED'
        if total > 0:
            if green == total:
                grade = 5.0
            elif yellow / total >= 0.6:
                grade = 3.0
            else:
                grade = round(5.0 * (green / total), 2)

            if green == total or grade >= 4.5:
                semaphore = 'GREEN'
            elif yellow / total >= 0.6 or grade >= 3.0:
                semaphore = 'YELLOW'
            else:
                semaphore = 'RED'

        return {
            'total': total,
            'green': green,
            'yellow': yellow,
            'red': red,
            'grade': grade,
            'semaphore': semaphore,
        }
class Exercise(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    deadline = models.DateTimeField(null=True, blank=True, help_text="Fecha límite de entrega")
    description = models.TextField(blank=True, null=True, help_text="Descripción del ejercicio")

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"{self.subject.code} - {self.name}"
    
    def is_overdue(self):
        """Check if exercise deadline has passed"""
        if not self.deadline:
            return False
        from django.utils import timezone
        return timezone.now() > self.deadline
    
    def days_until_deadline(self):
        """Return number of days until deadline (negative if overdue)"""
        if not self.deadline:
            return None
        from django.utils import timezone
        delta = self.deadline - timezone.now()
        return delta.days
    
    def deadline_status(self):
        """Return deadline status: 'OVERDUE', 'URGENT' (<=3 days), 'UPCOMING', or 'NONE'"""
        if not self.deadline:
            return 'NONE'
        days = self.days_until_deadline()
        if days < 0:
            return 'OVERDUE'
        elif days <= 3:
            return 'URGENT'
        else:
            return 'UPCOMING'


class StudentExerciseResult(models.Model):
    class Status(models.TextChoices):
        GREEN = 'GREEN', 'Verde'
        YELLOW = 'YELLOW', 'Amarillo'
        RED = 'RED', 'Rojo'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='results')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='results')
    status = models.CharField(max_length=10, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'exercise')
        indexes = [
            models.Index(fields=['enrollment', 'exercise']),
        ]

    def __str__(self) -> str:
        return f"{self.enrollment.student.email} - {self.exercise.name}: {self.status}"


class Notification(models.Model):
    """
    Model for in-app notifications.
    Notifies users about important events like enrollments, results updates, etc.
    """
    class NotificationType(models.TextChoices):
        ENROLLMENT = 'ENROLLMENT', 'Inscripción'
        RESULT_CREATED = 'RESULT_CREATED', 'Resultado Creado'
        RESULT_UPDATED = 'RESULT_UPDATED', 'Resultado Actualizado'
        EXERCISE_CREATED = 'EXERCISE_CREATED', 'Ejercicio Creado'
        GENERAL = 'GENERAL', 'General'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, null=True)  # URL to navigate to
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.title} ({'Leída' if self.is_read else 'No leída'})"
