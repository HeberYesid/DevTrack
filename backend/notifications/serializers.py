from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'recipient_email', 'type', 'title', 'message', 'link_url', 'is_read', 'created_at']
        read_only_fields = ['recipient', 'recipient_email', 'created_at']
