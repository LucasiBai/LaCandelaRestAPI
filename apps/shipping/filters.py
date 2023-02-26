from django.utils.translation import gettext_lazy as _
import django_filters.rest_framework as filters

from apps.api_root.utils import FilterMixins, FilterResultsFilterset

from .serializers import ShippingInfoSerializer


class ShippingInfoFilterset(FilterResultsFilterset, FilterMixins):
    """
    Shipping info filterset
    """
    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    user_id = filters.NumberFilter(field_name="user__id", lookup_expr="exact", label=_("User ID"))

    class Meta:
        model = ShippingInfoSerializer.Meta.model
        fields = [
            "user_id",
            "offset",
            "limit"
        ]


class MyInfoFilterset(FilterResultsFilterset, FilterMixins):
    """
    My info filterset
    """
    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    is_selected = filters.BooleanFilter(field_name="is_selected", label=_("Is selected?"))

    class Meta:
        model = ShippingInfoSerializer.Meta.model
        fields = [
            "is_selected",
            "offset",
            "limit"
        ]
