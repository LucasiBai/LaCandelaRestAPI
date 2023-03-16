from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.api_root.permissions import IsOwnData

from .serializers import FavouriteItemsSerializer


class FavouriteItemViewset(ModelViewSet):
    """
    Favourite Items API
    """
    serializer_class = FavouriteItemsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.all()

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "retrieve":
            permission_classes = [IsAuthenticated, IsOwnData]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
