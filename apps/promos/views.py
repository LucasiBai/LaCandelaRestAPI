from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import PromoSerializer
from .filters import PromoFilterSet


class PromoAPIViewset(ModelViewSet):
    """
    Promos API
    """
    model = PromoSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = PromoSerializer

    filterset_class = PromoFilterSet

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Returns Api list view
        """
        promos = self.filter_queryset(self.get_queryset())
        if promos:
            serializer = self.serializer_class(promos, many=promos)

            format_response = {
                "results": len(promos),
                "data": serializer.data
            }
            return Response(format_response, status=status.HTTP_200_OK)

        return Response({"message": "Not found promos."})
