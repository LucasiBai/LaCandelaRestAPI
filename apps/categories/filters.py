from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from .serializers import CategorySerializer
from apps.api_root.utils import FilterMixins, FilterResultsFilterset


class CategoryFilterset(FilterResultsFilterset, FilterMixins):
    """
    Categories Filterset
    """

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    parent_title = filters.CharFilter(
        field_name="title", lookup_expr="icontains", label=_("Parent Title")
    )

    class Meta:
        model = CategorySerializer.Meta.model
        fields = [
            "parent_title",
            "offset",
            "limit",
        ]
