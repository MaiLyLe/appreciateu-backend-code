from rest_framework.views import APIView
from user_recommendation.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CurrentUserView(APIView):
    """View for getting the current user"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Returns essential data for current user"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
