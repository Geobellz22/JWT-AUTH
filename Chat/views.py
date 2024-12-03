from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Conversation, Message, Notification
from .serializers import ConversationSerializer, MessageSerializer, NotificationSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(user=user) if not user.is_staff else Conversation.objects.all()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation")
        return Message.objects.filter(conversation=conversation_id)

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        self.create_notification_and_email(message)
        self.send_websocket_notification(message)

    def create_notification_and_email(self, message):
        conversation = message.conversation
        sender = message.sender
        recipient = conversation.agent if sender == conversation.user else conversation.user

        # Create a notification
        Notification.objects.create(
            user=recipient,
            conversation=conversation,
            message=f"New message from {sender.username}: {message.content}"
        )

        # Send email notification
        if recipient.email:
            send_mail(
                subject=f"New Message in Conversation {conversation.id}",
                message=message.content,
                from_email="support@matrixmomentum.com",
                recipient_list=[recipient.email],
                fail_silently=False,
            )

    def send_websocket_notification(self, message):
        # Send real-time WebSocket notification
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{message.conversation.id}'

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': message.sender.username,
                'timestamp': message.timestamp.isoformat(),
            }
        )


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Mark the notification as read
        serializer.save(is_read=True)