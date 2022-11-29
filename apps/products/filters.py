from django_filters import rest_framework as filters

from .serializers import ProductSerializer


class ProductsFilterSet(filters.FilterSet):
    """
    Filterset of Product model
    """

    title = filters.CharFilter(
        field_name="title", lookup_expr="contains", label="Title"
    )

    category = filters.CharFilter(
        field_name="category__title", lookup_expr="exact", label="Category"
    )

    min_price = filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Min Price"
    )
    max_price = filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Max Price"
    )

    # min_rate = filters.NumberFilter(
    #     field_name="rate", lookup_expr="gte", label="Min Rate"
    # )
    # max_rate = filters.NumberFilter(
    #     field_name="rate", lookup_expr="lte", label="Max Rate"
    # )

    class Meta:
        model = ProductSerializer.Meta.model
        fields = [
            "min_price",
            "max_price",
            "title",
            "category",
            # "min_rate",
            # "max_rate"
        ]
