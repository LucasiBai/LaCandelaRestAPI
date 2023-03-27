from django_filters import rest_framework as filters

from apps.api_root.utils import FilterMixins, FilterResultsFilterset

from .serializers import FavouriteItemsSerializer


class FavouriteItemsFilterset(FilterResultsFilterset, FilterMixins):
    """
    Favourite Item Filterset
    """

    customer_id = filters.NumberFilter(field_name="user__id", lookup_expr="exact")

    product_id = filters.NumberFilter(field_name="product__id", lookup_expr="exact")

    offset = filters.NumberFilter(method="query_offset")

    limit = filters.NumberFilter(method="query_limit")

    class Meta:
        model = FavouriteItemsSerializer.Meta.model
        fields = [
            "product_id",
            "customer_id",
            "offset",
            "limit"
        ]


class FavouriteItemsMyListFilterset(FilterResultsFilterset, FilterMixins):
    """
    Favourite Item My list action filter set
    """

    offset = filters.NumberFilter(method="query_offset")

    limit = filters.NumberFilter(method="query_limit")

    class Meta:
        model = FavouriteItemsSerializer.Meta.model
        fields = [
            "offset",
            "limit"
        ]
