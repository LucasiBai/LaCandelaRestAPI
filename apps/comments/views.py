from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from apps.api_root.permissions import IsOwnDataOrSuperuser
from apps.api_root.utils import FilterMethodsViewset
from .serializers import CommentSerializer
from .filters import CommentFilterset


class CommentViewset(FilterMethodsViewset):
    """
    Comment API Viewset
    """

    model = CommentSerializer.Meta.model
    queryset = model.objects.all()
    serializer_class = CommentSerializer
    filterset_class = CommentFilterset

    def get_permissions(self):
        """
        Gets custom permission for the view
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [AllowAny]
        elif self.action == "update" or self.action == "partial_update":
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsOwnDataOrSuperuser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Gets comments and results quantity
        """
        comments = self.filter_queryset(self.get_queryset())

        if comments:
            serializer = self.serializer_class(comments, many=True)

            export_data = {
                "results": self.results,
                "data": serializer.data,
            }

            return Response(export_data, status=status.HTTP_200_OK)

        return Response(
            {"results": 0, "message": "Not found comments."},
            status=status.HTTP_204_NO_CONTENT,
        )

    def create(self, request, *args, **kwargs):
        context = {"user": request.user, "action": "create"}

        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
