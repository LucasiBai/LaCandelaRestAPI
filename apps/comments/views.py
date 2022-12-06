from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .serializers import CommentSerializer


class CommentViewset(ModelViewSet):
    """
    Comment API Viewset
    """

    queryset = CommentSerializer.Meta.model.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        elif self.action == "update" or self.action == "partial_update":
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
