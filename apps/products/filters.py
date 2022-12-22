from django.utils.translation import gettext_lazy as _

import django_filters.rest_framework as filters

from .serializers import ProductSerializer
from apps.api_root.utils import FilterMethods


class ProductsFilterSet(filters.FilterSet, FilterMethods):
    """
    Filterset of Product model
    """

    title = filters.CharFilter(
        field_name="title", lookup_expr="icontains", label=_("Title")
    )

    category = filters.CharFilter(
        field_name="category__title", lookup_expr="iexact", label=_("Category")
    )

    min_price = filters.NumberFilter(
        field_name="price", lookup_expr="gte", label=_("Min Price")
    )
    max_price = filters.NumberFilter(
        field_name="price", lookup_expr="lte", label=_("Max Price")
    )

    min_rate = filters.NumberFilter(method="query_min_rate", label=_("Min Rate"))
    max_rate = filters.NumberFilter(method="query_max_rate", label=_("Max Rate"))

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    class Meta:
        model = ProductSerializer.Meta.model
        fields = [
            "title",
            "category",
            "min_price",
            "max_price",
            "offset",
            "limit",
        ]
