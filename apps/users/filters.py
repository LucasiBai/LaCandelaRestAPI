from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from apps.api_root.utils import FilterMethods


class UserAccountFilterset(filters.FilterSet, FilterMethods):
    """
    User Account Filterset
    """

    offset = filters.NumberFilter(field_name="id", lookup_expr="gte", label=_("Offset"))

    limit = filters.NumberFilter(
        field_name="id", method="query_limit", label=_("Limit")
    )

    class Meta:
        model = get_user_model()
        fields = [
            "offset",
            "limit",
        ]
