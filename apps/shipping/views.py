from rest_framework.viewsets import ModelViewSet

from .serializers import ShippingInfoSerializer


class ShippingInfoViewset(ModelViewSet):
    """
    Shipping Info Viewset
    """
    model = ShippingInfoSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = ShippingInfoSerializer
