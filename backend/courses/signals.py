from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment, StudentExerciseResult, Exercise, Notification


@receiver(post_save, sender=Enrollment)
def notify_enrollment_created(sender, instance: Enrollment, created: bool, **kwargs):
    """Notify student and teacher when a new enrollment is created"""
    if not created:
        return
    try:
        subject = instance.subject
        # Notify student
        Notification.objects.create(
            user=instance.student,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title=f'📚 Inscrito en {subject.code}',
            message=f'Has sido inscrito en {subject.name}. Profesor: {subject.teacher.email}',
            link=f'/subjects/{subject.id}',
        )
        # Notify teacher
        Notification.objects.create(
            user=subject.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title=f'👥 Nuevo estudiante en {subject.code}',
            message=f'{instance.student.email} fue inscrito en tu materia.',
            link=f'/subjects/{subject.id}',
        )
    except Exception as e:
        # Avoid breaking main flow on notification errors
        print(f"Error creating enrollment notification: {e}")


@receiver(post_save, sender=StudentExerciseResult)
def notify_result_updated(sender, instance: StudentExerciseResult, created: bool, **kwargs):
    """Notify student and teacher when a result is created or updated"""
    try:
        enrollment = instance.enrollment
        subject = enrollment.subject
        
        status_emoji = {
            'GREEN': '🟢',
            'YELLOW': '🟡',
            'RED': '🔴'
        }.get(instance.status, '📊')
        
        if created:
            # Notify student about new result
            Notification.objects.create(
                user=enrollment.student,
                notification_type=Notification.NotificationType.RESULT_CREATED,
                title=f'{status_emoji} Nuevo resultado en {subject.code}',
                message=f"Ejercicio '{instance.exercise.name}' calificado como {instance.status}.",
                link=f'/subjects/{subject.id}',
            )
        else:
            # Notify student about result update
            Notification.objects.create(
                user=enrollment.student,
                notification_type=Notification.NotificationType.RESULT_UPDATED,
                title=f'{status_emoji} Resultado actualizado en {subject.code}',
                message=f"El ejercicio '{instance.exercise.name}' fue actualizado a {instance.status}.",
                link=f'/subjects/{subject.id}',
            )
    except Exception as e:
        print(f"Error creating result notification: {e}")


@receiver(post_save, sender=Exercise)
def notify_exercise_created(sender, instance: Exercise, created: bool, **kwargs):
    """Notify enrolled students when a new exercise is created"""
    if not created:
        return
    try:
        subject = instance.subject
        enrollments = subject.enrollments.select_related('student').all()
        
        # Notify all enrolled students
        notifications = []
        for enrollment in enrollments:
            notifications.append(
                Notification(
                    user=enrollment.student,
                    notification_type=Notification.NotificationType.EXERCISE_CREATED,
                    title=f'📝 Nuevo ejercicio en {subject.code}',
                    message=f"Se creó el ejercicio '{instance.name}' en {subject.name}.",
                    link=f'/subjects/{subject.id}',
                )
            )
        
        # Bulk create for better performance
        if notifications:
            Notification.objects.bulk_create(notifications)
    except Exception as e:
        print(f"Error creating exercise notification: {e}")
