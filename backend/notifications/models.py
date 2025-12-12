from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    class Type(models.TextChoices):
        ENROLLMENT_CREATED = 'ENROLLMENT_CREATED', 'Inscripción creada'
        RESULTS_UPDATED = 'RESULTS_UPDATED', 'Resultados actualizados'
        REPORT_READY = 'REPORT_READY', 'Reporte listo'
        NEW_MESSAGE = 'NEW_MESSAGE', 'Nuevo mensaje'
        GENERAL = 'GENERAL', 'General'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=40, choices=Type.choices, default=Type.GENERAL)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    link_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"
