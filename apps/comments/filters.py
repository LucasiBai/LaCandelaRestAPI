from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from .serializers import CommentSerializer
from apps.api_root.utils import FilterMethods


class CommentFilterset(filters.FilterSet, FilterMethods):
    """
    Comments Api Filterset
    """

    user = filters.NumberFilter(
        field_name="user__pk", method="get_by_id", label=_("User Id")  # user id filter
    )
    product = filters.NumberFilter(
        field_name="product__pk",
        method="get_by_id",  # product id filter
        label=_("Product Id"),
    )

    min_rate = filters.NumberFilter(
        field_name="rate", lookup_expr="gte", label=_("Min Rate")
    )
    max_rate = filters.NumberFilter(
        field_name="rate", lookup_expr="lte", label=_("Max Rate")  # max rate filter
    )

    offset = filters.NumberFilter(
        method="query_offset", label=_("Offset")  # offset filter
    )

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))  # limit filter

    class Meta:
        model = CommentSerializer.Meta.model
        fields = [
            "user",
            "product",
            "min_rate",
            "max_rate",
            "offset",
            "limit",
        ]
