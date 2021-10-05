import requests
from rest_framework import viewsets, mixins, status
from message.serializers import MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Message
from django.contrib.auth import get_user_model

MAX_TRIES = 3


class CreateListMessageView(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            ):
    """View class of Message model"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, serializer):
        """Creates Message object only if called sentiment analysis API
        detects no negative language"""
        receiver_id = self.request.data['receiver_id']
        text = self.request.data['text']
        sentiment_analysis_api_attempts = 0
        url_text_str = text.replace(" ", "%20")

        while sentiment_analysis_api_attempts < MAX_TRIES:
            r = requests.get(
                "https://twinword-sentiment-analysis.p.rapidapi.com/analyze/?text=" + url_text_str,
                headers={"x-rapidapi-host": "twinword-sentiment-analysis.p.rapidapi.com",
                         "x-rapidapi-key": "ea475bcd49mshc86d688561440c5p1e9d92jsn08f2cd73920a"},
                timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data["type"] == "positive" or data["type"] == "neutral":
                    receiver = get_user_model().objects.get(id=receiver_id)
                    Message.objects.create(sender=self.request.user, receiver=receiver, text=text)
                    return Response({"detail": "Message sent."}, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "Inadequate content detected. \
                                                We cannot send message. Please, Try again."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                sentiment_analysis_api_attempts += 1
        return Response({"detail": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Returns all messages of logged-in user ordered by creation time from newest to oldest"""
        user = self.request.user
        return user.messages_received.order_by("-timestamp").all()

    def list_messages_for_receiver(self, request):
        """Returns list of messages sent to logged-in user"""
        queryset = self.get_queryset()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def mark_message_seen(self, request, pk=None, url_path='mark-message-seen'):
        """Updates message object's is_seen attribute to true"""
        Message.objects.filter(pk=pk).update(is_seen=True)
        updated_model = Message.objects.get(pk=pk)
        serializer = MessageSerializer(updated_model, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def number_of_unread_messages(self, request, pk=None, url_path='number_of_unread_messages'):
        """Returns number of messages marked as is_seen being false"""
        number_unread = self.request.user.messages_received.filter(is_seen=False).count()
        number_total = self.request.user.messages_received.count()
        return Response({"unread_messages": number_unread, "total_number": number_total},
                        status=status.HTTP_200_OK)
