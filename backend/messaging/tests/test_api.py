import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from messaging.models import Conversation, Message

User = get_user_model()

@pytest.mark.django_db
class TestConversationAPI:
    def test_list_conversations(self, api_client, student_user, teacher_user):
        """Test listing conversations for a user"""
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        # Another conversation for teacher only (with another student)
        try:
            other_student = User.objects.get(username='other_student')
        except User.DoesNotExist:
            other_student = User.objects.create_user(username='other_student', email='other@test.com', password='password123', role='STUDENT')
            
        other_conv = Conversation.objects.create()
        other_conv.participants.add(teacher_user, other_student)
        
        # Login as student
        api_client.force_authenticate(user=student_user)
        
        url = reverse('conversation-list')
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == conversation.id

    def test_start_conversation_success(self, api_client, student_user, teacher_user):
        """Test starting a new conversation"""
        api_client.force_authenticate(user=student_user)
        
        url = reverse('conversation-start')
        data = {'recipient_id': teacher_user.id}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Conversation.objects.count() == 1
        assert teacher_user in Conversation.objects.first().participants.all()

    def test_start_conversation_existing(self, api_client, student_user, teacher_user):
        """Test starting a conversation that already exists returns the existing one"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        api_client.force_authenticate(user=student_user)
        
        url = reverse('conversation-start')
        data = {'recipient_id': teacher_user.id}
        
        response = api_client.post(url, data, format='json')
        # View returns 200 for existing
        assert response.status_code == 200
        assert response.data['id'] == conversation.id
        # Should not create duplicate
        assert Conversation.objects.count() == 1

    def test_start_conversation_self_error(self, api_client, student_user):
        """Test cannot start conversation with self"""
        api_client.force_authenticate(user=student_user)
        
        url = reverse('conversation-start')
        data = {'recipient_id': student_user.id}
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == 400

    def test_read_all_messages(self, api_client, student_user, teacher_user):
        """Test marking all messages as read"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        # Teacher sends message to student
        Message.objects.create(conversation=conversation, sender=teacher_user, content="Msg 1")
        Message.objects.create(conversation=conversation, sender=teacher_user, content="Msg 2")
        
        api_client.force_authenticate(user=student_user)
        
        url = reverse('conversation-read-all', args=[conversation.id])
        response = api_client.post(url)
        
        assert response.status_code == 200
        assert Message.objects.filter(is_read=True).count() == 2


@pytest.mark.django_db
class TestMessageAPI:
    def test_send_message(self, api_client, student_user, teacher_user):
        """Test sending a message"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        api_client.force_authenticate(user=student_user)
        
        url = reverse('message-list')
        data = {
            'conversation_id': conversation.id,
            'content': 'Hello Professor'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert response.data['content'] == 'Hello Professor'
        assert Message.objects.count() == 1
        assert Message.objects.first().sender == student_user

    def test_send_message_not_participant(self, api_client, student_user):
        """Test cannot send message to conversation user is not part of"""
        # Create conversation between two others
        other1 = User.objects.create_user(username='u1', email='u1@t.com', password='p', role='STUDENT')
        other2 = User.objects.create_user(username='u2', email='u2@t.com', password='p', role='TEACHER')
        conversation = Conversation.objects.create()
        conversation.participants.add(other1, other2)
        
        api_client.force_authenticate(user=student_user)
        
        url = reverse('message-list')
        data = {
            'conversation_id': conversation.id,
            'content': 'Intruder message'
        }
        
        response = api_client.post(url, data, format='json')
        
        # View returns 404 because it filters conversation by participants
        assert response.status_code == 404

    def test_list_messages_security(self, api_client, student_user):
        """Test cannot verify messages of other conversations"""
        other3 = User.objects.create_user(username='u3', email='u3@t.com', password='p', role='STUDENT')
        other4 = User.objects.create_user(username='u4', email='u4@t.com', password='p', role='TEACHER')
        conversation = Conversation.objects.create()
        conversation.participants.add(other3, other4)
        Message.objects.create(conversation=conversation, sender=other3, content="Private")
        
        api_client.force_authenticate(user=student_user)
        
        # Try to list messages filtering by that conversation ID
        url = reverse('message-list')
        response = api_client.get(f"{url}?conversation={conversation.id}")
        
        # Should return empty list or 404, depending on implementation
        # Our implementation creates queryset then filters. 
        # queryset = Message.objects.filter(conversation__participants=self.request.user)
        # So it should be empty
        assert len(response.data) == 0
