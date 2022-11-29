from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from .filters import ProductsFilterSet
from apps.products.serializers import ProductSerializer
from db.models import Product


class ProductsViewSet(ModelViewSet):
    """
    Products model viewset
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductsFilterSet

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
