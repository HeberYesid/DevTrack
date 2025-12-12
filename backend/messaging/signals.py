from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from notifications.models import Notification

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        # Update conversation timestamp
        instance.conversation.save()
        
        # Notify all participants except the sender
        for participant in instance.conversation.participants.all():
            if participant != instance.sender:
                Notification.objects.create(
                    recipient=participant,
                    type=Notification.Type.NEW_MESSAGE,
                    title=f"Nuevo mensaje de {instance.sender.first_name or instance.sender.email}",
                    message=instance.content[:50] + "..." if len(instance.content) > 50 else instance.content,
                    link_url=f"/messages/{instance.conversation.id}"
                )
