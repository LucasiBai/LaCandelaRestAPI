from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from .serializers import CommentSerializer


class CommentFilterset(filters.FilterSet):
    """
    Comments Api Filterset
    """

    user = filters.NumberFilter(
        field_name="user__pk", method="get_by_id", label=_("User Id")
    )
    product = filters.NumberFilter(
        field_name="product__pk", method="get_by_id", label=_("Product Id")
    )

    def get_by_id(self, queryset, name, value):
        """
        Gets the queryset with the entered id
        """
        filter_value = {name: value}
        return queryset.filter(**filter_value)

    class Meta:
        model = CommentSerializer.Meta.model
        fields = [
            "user",
            "product",
        ]
