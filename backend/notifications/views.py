from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        # Not exposed publicly; reserved for system events (signals)
        serializer.save(recipient=self.request.user)

    def update(self, request, *args, **kwargs):
        # Limit updates to 'is_read'
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {'is_read': request.data.get('is_read', True)}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread': count})

    @decorators.action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        updated = qs.update(is_read=True)
        return Response({'updated': updated})
