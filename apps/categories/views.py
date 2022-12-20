from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .serializers import CategorySerializer


class CategoryViewset(ModelViewSet):
    queryset = CategorySerializer.Meta.model.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
