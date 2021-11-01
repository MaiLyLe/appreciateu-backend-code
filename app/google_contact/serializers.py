from rest_framework import serializers
from core.models import GoogleContact
from user_recommendation.serializers import UserSerializer


class GoogleContactSerializer(serializers.ModelSerializer):
    """Serializer for Google Contact Model"""

    class Meta:
        """Meta class of GoogleContact serializer"""
        model = GoogleContact
        fields = ('contact_owner', 'owned_contact')

    def to_representation(self, instance):
        """Overridden function to make sure multiple GoogleContact objects can be saved"""
        response = super().to_representation(instance)
        response['owned_contact'] = UserSerializer(instance.owned_contact).data
        response['contact_owner'] = UserSerializer(instance.contact_owner).data
        return response
