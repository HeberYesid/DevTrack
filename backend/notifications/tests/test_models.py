import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


@pytest.mark.django_db
class TestNotificationModel:
    """Tests for Notification model"""
    
    def test_create_notification(self, student_user):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=student_user,
            title='New Assignment',
            message='You have a new assignment in Math',
            type=Notification.Type.GENERAL
        )
        assert notification.recipient == student_user
        assert notification.title == 'New Assignment'
        assert not notification.is_read
    
    def test_notification_str_representation(self, student_user):
        """Test string representation of notification"""
        notification = Notification.objects.create(
            recipient=student_user,
            title='Test Notification',
            message='Test message',
            type=Notification.Type.GENERAL
        )
        assert 'Test Notification' in str(notification)
        assert student_user.email in str(notification)
    
    def test_mark_notification_as_read(self, student_user):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            recipient=student_user,
            title='Test',
            message='Test message'
        )
        assert not notification.is_read
        
        notification.is_read = True
        notification.save()
        assert notification.is_read
    
    def test_notification_types(self, student_user):
        """Test different notification types"""
        types = [
            Notification.Type.ENROLLMENT_CREATED,
            Notification.Type.RESULTS_UPDATED,
            Notification.Type.REPORT_READY,
            Notification.Type.GENERAL
        ]
        
        for notif_type in types:
            Notification.objects.create(
                recipient=student_user,
                title=f'{notif_type} Notification',
                message='Test',
                type=notif_type
            )
        
        assert Notification.objects.filter(recipient=student_user).count() == len(types)
