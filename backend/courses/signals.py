from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Enrollment, StudentExerciseResult, Exercise, Subject
from notifications.models import Notification

User = get_user_model()


@receiver(post_save, sender=User)
def enroll_new_student_in_demo(sender, instance, created, **kwargs):
    """Enroll new students in a demo subject automatically"""
    if created and instance.role == 'STUDENT':
        # Find or create Demo subject
        demo_subject = Subject.objects.filter(code='DEMO-101').first()
        
        if not demo_subject:
            # Try to find a teacher or admin to own the subject
            teacher = User.objects.filter(role__in=['TEACHER', 'ADMIN']).first()
            if teacher:
                demo_subject = Subject.objects.create(
                    name='Materia de Demostración',
                    code='DEMO-101',
                    teacher=teacher
                )
                # Create some demo exercises
                Exercise.objects.create(
                    subject=demo_subject,
                    name='Ejercicio 1: Bienvenida',
                    order=1,
                    description='¡Bienvenido a DevTrack! Este es un ejercicio de ejemplo para que conozcas la plataforma.'
                )
                Exercise.objects.create(
                    subject=demo_subject,
                    name='Ejercicio 2: Tu primer entregable',
                    order=2,
                    description='Este es otro ejercicio de ejemplo. En una materia real, aquí verías los detalles de la tarea.'
                )
        
        if demo_subject:
            Enrollment.objects.get_or_create(
                student=instance,
                subject=demo_subject
            )


@receiver(post_save, sender=Enrollment)
def notify_enrollment_created(sender, instance: Enrollment, created: bool, **kwargs):
    """Notify student and teacher when a new enrollment is created"""
    if not created:
        return
    try:
        subject = instance.subject
        # Notify student
        Notification.objects.create(
            recipient=instance.student,
            type=Notification.Type.ENROLLMENT_CREATED,
            title=f'📚 Inscrito en {subject.code}',
            message=f'Has sido inscrito en {subject.name}. Profesor: {subject.teacher.email}',
            link_url=f'/subjects/{subject.id}',
        )
        # Notify teacher
        Notification.objects.create(
            recipient=subject.teacher,
            type=Notification.Type.ENROLLMENT_CREATED,
            title=f'👥 Nuevo estudiante en {subject.code}',
            message=f'{instance.student.email} fue inscrito en tu materia.',
            link_url=f'/subjects/{subject.id}',
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
            'RED': '🔴',
            'SUBMITTED': '🔵'
        }.get(instance.status, '📊')
        
        if instance.status == 'SUBMITTED':
            # Notify Teacher about submission
            Notification.objects.create(
                recipient=subject.teacher,
                type=Notification.Type.GENERAL, # Fallback as SUBMISSION_CREATED is not in current Type enum for notifications app?
                title=f'📄 Nueva entrega en {subject.code}',
                message=f"El estudiante {enrollment.student.email} ha entregado el ejercicio '{instance.exercise.name}'.",
                link_url=f'/subjects/{subject.id}',
            )

        if created:
            # Notify student about new result
            Notification.objects.create(
                recipient=enrollment.student,
                type=Notification.Type.GENERAL, # Fallback
                title=f'{status_emoji} Nuevo resultado en {subject.code}',
                message=f"Ejercicio '{instance.exercise.name}' calificado como {instance.status}.",
                link_url=f'/subjects/{subject.id}',
            )
        else:
            # Notify student about result update
            Notification.objects.create(
                recipient=enrollment.student,
                type=Notification.Type.RESULTS_UPDATED,
                title=f'{status_emoji} Resultado actualizado en {subject.code}',
                message=f"El ejercicio '{instance.exercise.name}' fue actualizado a {instance.status}.",
                link_url=f'/subjects/{subject.id}',
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
                    recipient=enrollment.student,
                    type=Notification.Type.GENERAL, # Fallback
                    title=f'Nuevo ejercicio en {subject.code}',
                    message=f"Se creó el ejercicio '{instance.name}' en {subject.name}.",
                    link_url=f'/subjects/{subject.id}',
                )
            )
        
        # Bulk create for better performance
        if notifications:
            Notification.objects.bulk_create(notifications)
    except Exception as e:
        print(f"Error creating exercise notification: {e}")
