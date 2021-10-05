from rest_framework import serializers
from core.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message Model"""
    number_unread_messages = serializers.SerializerMethodField()

    class Meta:
        """Meta class of Message serializer"""
        model = Message
        fields = ('text', 'timestamp', 'id', 'is_seen', 'avatar_num', 'number_unread_messages')
        read_only_fields = ('number_unread_messages',)

    def get_number_unread_messages(self, obj):
        """Serializes number of Message objects where is_seen is false"""
        request = self.context.get('request', None)
        if request:
            return request.user.messages_received.filter(is_seen=False).count()
