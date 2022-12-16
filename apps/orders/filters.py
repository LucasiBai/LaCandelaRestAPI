from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from .serializers import OrderSerializer
from apps.api_root.utils import FilterMethods


class OrderFilterset(filters.FilterSet, FilterMethods):
    """
    Order Filterset
    """

    user = filters.NumberFilter(
        field_name="buyer__pk", method="get_by_id", label=_("User Id")
    )

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    class Meta:
        model = OrderSerializer.Meta.model
        fields = [
            "user",
            "offset",
            "limit",
        ]
