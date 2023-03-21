from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .permissions import IsOwnFavItemOrSuperuser
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
        if self.action == "retrieve" or self.action == "partial_update" or self.action == "update" or self.action == "get_my_list" or self.action == "get_my_list_detail":
            permission_classes = [IsAuthenticated, IsOwnFavItemOrSuperuser]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Gets fav items and result quantity response

        Returns:
            generated response
        """
        fav_list = self.filter_queryset(self.get_queryset())

        if fav_list:
            serializer = self.serializer_class(fav_list, many=True)

            res_data = {
                "results": len(fav_list),
                "data": serializer.data,
            }

            return Response(res_data, status=status.HTTP_200_OK)

        return Response({"message": "Not found fav items."}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update method not allowed
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update method not allowed
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=["get", "post"],
        url_path="my-list",
    )
    def get_my_list(self, request, *args, **kwargs):
        """
        Gets current user list and return response
        """
        user = request.user

        if request.method == "GET":
            user_fav_list = self.filter_queryset(self.model.objects.get_user_fav(user))

            if user_fav_list:
                serializer = self.serializer_class(user_fav_list, many=True)

                response_data = {
                    "results": len(user_fav_list),
                    "data": serializer.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            return Response({"message": "Not found fav items."}, status=status.HTTP_200_OK)

        elif request.method == "POST":
            product = request.data.get("product", None)

            if not product:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            data = {
                "user": user.id,
                "product": product
            }

            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=["delete"],
        url_path="my-list",
    )
    def get_my_list_detail(self, request, pk, *args, **kwargs):
        """
        Gets only current user detail fav item
        """
        user = request.user

        if request.method == "DELETE":
            fav_item = get_object_or_404(self.model, user=user, pk=pk)

            fav_item.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
