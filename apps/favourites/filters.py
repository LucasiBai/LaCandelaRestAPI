from django_filters import rest_framework as filters

from apps.api_root.utils import FilterMixins, FilterResultsFilterset

from .serializers import FavouriteItemsSerializer


class FavouriteItemsFilterset(FilterResultsFilterset, FilterMixins):
    """
    Favourite Item Filterset
    """

    customer_id = filters.NumberFilter(field_name="user__id", lookup_expr="exact")

    offset = filters.NumberFilter(method="query_offset")

    limit = filters.NumberFilter(method="query_limit")

    class Meta:
        model = FavouriteItemsSerializer.Meta.model
        fields = [
            "customer_id",
            "offset",
            "limit"
        ]
