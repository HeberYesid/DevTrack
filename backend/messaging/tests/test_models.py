import pytest
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Message

User = get_user_model()

@pytest.mark.django_db
class TestConversationModel:
    def test_create_conversation(self, student_user, teacher_user):
        """Test creating a conversation between two users"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        assert conversation.participants.count() == 2
        assert student_user in conversation.participants.all()
        assert teacher_user in conversation.participants.all()
        
    def test_conversation_str(self):
        """Test string representation of conversation"""
        conversation = Conversation.objects.create()
        assert f"Conversation {conversation.id}" == str(conversation)

@pytest.mark.django_db
class TestMessageModel:
    def test_create_message(self, student_user, teacher_user):
        """Test creating a message"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=student_user,
            content="Hello teacher"
        )
        
        assert message.conversation == conversation
        assert message.sender == student_user
        assert message.content == "Hello teacher"
        assert message.is_read is False
        
    def test_message_str(self, student_user, teacher_user):
        """Test string representation of message"""
        conversation = Conversation.objects.create()
        conversation.participants.add(student_user, teacher_user)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=student_user,
            content="Hello"
        )
        
        assert str(student_user) in str(message)
        assert str(message.created_at) in str(message)
