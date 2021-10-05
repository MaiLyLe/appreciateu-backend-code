from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from core.models import GoogleContact
from rest_framework import status, viewsets
from googlecontact.serializers import GoogleContactSerializer


class GoogleContactViewSet(viewsets.ModelViewSet):
    """View class for GoogleContact model"""
    serializer_class = GoogleContactSerializer
    permission_classes = (IsAuthenticated,)
    queryset = GoogleContact.objects.all()

    def create(self, request, *args, **kwargs):
        """Customized create function that takes multiple objects and checks
        wether the contact exists in the user model before saving"""
        request.user.google_email = request.data[0]['contact_owner']
        request.user.save()
        request.user.google_last_updated = now()
        request.user.save()
        existing_contacts = []
        if request.data[0]['owned_contact']:
            for entry in request.data:
                google_mail_exists = get_user_model().objects.filter(
                    google_email=entry['owned_contact']).exists()
                main_email_exists = get_user_model().objects.filter(
                    email=entry['owned_contact']).exists()
                if google_mail_exists or main_email_exists:
                    existing_contact = entry
                    pk = None
                    if google_mail_exists:
                        pk = get_user_model().objects.get(
                            google_email=entry['owned_contact']).pk
                    elif main_email_exists:
                        pk = get_user_model().objects.get(
                            email=entry['owned_contact']).pk

                    existing_contact['owned_contact'] = pk
                    existing_contact['contact_owner'] = request.user.pk
                    if not GoogleContact.objects.filter(contact_owner=request.user.pk,
                                                        owned_contact=pk).exists():
                        existing_contacts.append(existing_contact)
        serializer = self.get_serializer(data=existing_contacts,
                                         many=isinstance(existing_contacts, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
