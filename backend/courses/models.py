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

    class Meta:
        unique_together = ('subject', 'name')
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"{self.subject.code} | {self.name}"


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
