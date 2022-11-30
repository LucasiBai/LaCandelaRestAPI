import django_filters.rest_framework as filters
from django.utils.translation import gettext_lazy as _

from .serializers import ProductSerializer

from .utils import get_validated_rate_products_pk


class ProductsFilterSet(filters.FilterSet):
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

    offset = filters.NumberFilter(field_name="id", lookup_expr="gte", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    def query_limit(self, queryset, name, value):
        """
        Limits the returned queryset
        """
        return queryset[:value]

    def query_min_rate(self, queryset, name, value):
        """
        Gets the returned products greater or equal than value
        """

        validated_id_products = get_validated_rate_products_pk("gte", queryset, value)

        return queryset.filter(pk__in=validated_id_products)

    def query_max_rate(self, queryset, name, value):
        """
        Gets the returned products lower or equal than value
        """
        validated_id_products = get_validated_rate_products_pk("lte", queryset, value)

        return queryset.filter(pk__in=validated_id_products)

    class Meta:
        model = ProductSerializer.Meta.model
        fields = ["title", "category", "min_price", "max_price", "offset", "limit"]
