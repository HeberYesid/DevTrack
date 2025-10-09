import pytest
from django.urls import reverse
from notifications.models import Notification


@pytest.mark.django_db
class TestNotificationAPI:
    """Tests for Notification API endpoints"""
    
    def test_list_my_notifications(self, authenticated_client, student_user):
        """Test listing user's notifications"""
        Notification.objects.create(
            user=student_user,
            title='Notification 1',
            message='Message 1',
            type='INFO'
        )
        Notification.objects.create(
            user=student_user,
            title='Notification 2',
            message='Message 2',
            type='ASSIGNMENT'
        )
        
        url = reverse('notification-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 2
    
    def test_unread_count(self, authenticated_client, student_user):
        """Test getting unread notifications count"""
        Notification.objects.create(
            user=student_user,
            title='Unread 1',
            message='Message',
            read=False
        )
        Notification.objects.create(
            user=student_user,
            title='Unread 2',
            message='Message',
            read=False
        )
        Notification.objects.create(
            user=student_user,
            title='Read',
            message='Message',
            read=True
        )
        
        url = reverse('notification-unread-count')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 2
    
    def test_mark_notification_as_read(self, authenticated_client, student_user):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=student_user,
            title='Test',
            message='Message',
            read=False
        )
        
        url = reverse('notification-detail', kwargs={'pk': notification.pk})
        data = {'read': True}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == 200
        notification.refresh_from_db()
        assert notification.read
    
    def test_mark_all_as_read(self, authenticated_client, student_user):
        """Test marking all notifications as read"""
        Notification.objects.create(
            user=student_user,
            title='Notification 1',
            message='Message',
            read=False
        )
        Notification.objects.create(
            user=student_user,
            title='Notification 2',
            message='Message',
            read=False
        )
        
        url = reverse('notification-mark-all-read')
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        unread = Notification.objects.filter(user=student_user, read=False).count()
        assert unread == 0
    
    def test_cannot_see_other_users_notifications(self, authenticated_client, student_user, teacher_user):
        """Test that users can only see their own notifications"""
        Notification.objects.create(
            user=teacher_user,
            title='Teacher Notification',
            message='Message'
        )
        
        url = reverse('notification-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 0
