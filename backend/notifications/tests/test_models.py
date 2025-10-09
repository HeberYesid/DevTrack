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
            user=student_user,
            title='New Assignment',
            message='You have a new assignment in Math',
            type='ASSIGNMENT'
        )
        assert notification.user == student_user
        assert notification.title == 'New Assignment'
        assert not notification.read
    
    def test_notification_str_representation(self, student_user):
        """Test string representation of notification"""
        notification = Notification.objects.create(
            user=student_user,
            title='Test Notification',
            message='Test message',
            type='INFO'
        )
        assert 'Test Notification' in str(notification)
    
    def test_mark_notification_as_read(self, student_user):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=student_user,
            title='Test',
            message='Test message'
        )
        assert not notification.read
        
        notification.read = True
        notification.save()
        assert notification.read
    
    def test_notification_types(self, student_user):
        """Test different notification types"""
        types = ['INFO', 'ASSIGNMENT', 'GRADE', 'ANNOUNCEMENT']
        
        for notif_type in types:
            Notification.objects.create(
                user=student_user,
                title=f'{notif_type} Notification',
                message='Test',
                type=notif_type
            )
        
        assert Notification.objects.filter(user=student_user).count() == len(types)
