from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from apps.api_root.utils import FilterMethodsViewset
from .serializers import CategorySerializer
from .filters import CategoryFilterset


class CategoryViewset(FilterMethodsViewset):
    """
    Category API Viewset
    """

    model = CategorySerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilterset

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
        Gets only parent categories
        """
        categories = self.filter_queryset(self.get_queryset().filter(parent=None))

        context = {"action": "list"}

        if categories:
            serializer = self.serializer_class(categories, context=context, many=True)

            export_data = {
                "results": self.results,
                "data": serializer.data,
            }

            return Response(export_data, status=status.HTTP_200_OK)

        return Response(
            {"message": "Not found categories."}, status=status.HTTP_204_NO_CONTENT
        )
