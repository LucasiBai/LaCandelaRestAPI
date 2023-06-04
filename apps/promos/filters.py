from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from apps.api_root.utils import FilterMixins, FilterResultsFilterset

from .meta import get_app_model


class PromoFilterSet(FilterResultsFilterset, FilterMixins):
    """
    Promo Model Filterset
    """

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    class Meta:
        model = get_app_model()
        fields = [
            "offset",
            "limit"
        ]
