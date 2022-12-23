from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from apps.api_root.utils import FilterMethods
from .serializers import UserAccountSerializer


class UserAccountFilterset(filters.FilterSet, FilterMethods):
    """
    User Account Filterset
    """

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(
        field_name="id", method="query_limit", label=_("Limit")
    )

    class Meta:
        model = UserAccountSerializer.Meta.model
        fields = [
            "offset",
            "limit",
        ]
