from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment, StudentExerciseResult


@receiver(post_save, sender=Enrollment)
def notify_enrollment_created(sender, instance: Enrollment, created: bool, **kwargs):
    if not created:
        return
    try:
        from notifications.models import Notification
        subject = instance.subject
        # Notify student
        Notification.objects.create(
            recipient=instance.student,
            type=Notification.Type.ENROLLMENT_CREATED,
            title=f'Te inscribieron en {subject.code} - {subject.name}',
            message='Has sido inscrito en una nueva materia.',
            link_url=f'/subjects/{subject.id}',
        )
        # Notify teacher
        Notification.objects.create(
            recipient=subject.teacher,
            type=Notification.Type.ENROLLMENT_CREATED,
            title=f'Nuevo estudiante inscrito en {subject.code}',
            message=f'{instance.student.email} fue inscrito.',
            link_url=f'/subjects/{subject.id}',
        )
    except Exception:
        # Avoid breaking main flow on notification errors
        pass


@receiver(post_save, sender=StudentExerciseResult)
def notify_result_updated(sender, instance: StudentExerciseResult, created: bool, **kwargs):
    try:
        from notifications.models import Notification
        enrollment = instance.enrollment
        subject = enrollment.subject
        title = 'Resultado nuevo' if created else 'Resultado actualizado'
        message = f"Ejercicio '{instance.exercise.name}' marcado como {instance.status}."
        # Notify student
        Notification.objects.create(
            recipient=enrollment.student,
            type=Notification.Type.RESULTS_UPDATED,
            title=f'{title} en {subject.code}',
            message=message,
            link_url=f'/subjects/{subject.id}',
        )
        # Notify teacher
        Notification.objects.create(
            recipient=subject.teacher,
            type=Notification.Type.RESULTS_UPDATED,
            title=f'{title} en {subject.code}',
            message=f"{enrollment.student.email}: {message}",
            link_url=f'/subjects/{subject.id}',
        )
    except Exception:
        pass
