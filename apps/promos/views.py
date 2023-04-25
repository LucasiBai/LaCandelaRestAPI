from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .serializers import PromoSerializer


class PromoAPIViewset(ModelViewSet):
    """
    Promos API
    """
    model = PromoSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = PromoSerializer

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
