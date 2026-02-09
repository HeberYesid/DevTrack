from rest_framework import viewsets, permissions, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiTypes
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CreateMessageSerializer, UserSimpleSerializer

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    @extend_schema(
        summary="Mark conversation as read",
        request=None,
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['post'])
    def read_all(self, request, pk=None):
        conversation = self.get_object()
        conversation.messages.exclude(sender=request.user).update(is_read=True)
        return Response({'status': 'marked as read'})

    @extend_schema(
        summary="Start conversation",
        request=inline_serializer(
            name="StartConversationRequest",
            fields={"recipient_id": serializers.IntegerField()},
        ),
        responses={201: ConversationSerializer},
    )
    @action(detail=False, methods=['post'])
    def start(self, request):
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if recipient == request.user:
            return Response({'error': 'Cannot message yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if conversation already exists
        conversations = Conversation.objects.filter(participants=request.user).filter(participants=recipient)
        if conversations.exists():
            return Response(ConversationSerializer(conversations.first(), context={'request': request}).data)

        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        return Response(ConversationSerializer(conversation, context={'request': request}).data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = Message.objects.filter(conversation__participants=self.request.user)
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        return queryset

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response({'error': 'conversation_id and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

class UserSearchViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSimpleSerializer
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        # Exclude self
        return User.objects.exclude(id=self.request.user.id)
