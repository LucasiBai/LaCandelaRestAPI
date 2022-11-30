import django_filters.rest_framework as filters
from django.utils.translation import gettext_lazy as _

from .serializers import ProductSerializer


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

    class Meta:
        model = ProductSerializer.Meta.model
        fields = [
            "title",
            "category",
            "min_price",
            "max_price",
        ]
