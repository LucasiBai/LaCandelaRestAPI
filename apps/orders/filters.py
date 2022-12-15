from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from .serializers import OrderSerializer


class OrderFilterset(filters.FilterSet):
    """
    Order Filterset
    """

    user = filters.NumberFilter(
        field_name="buyer__pk", method="get_by_id", label=_("User Id")
    )

    def get_by_id(self, queryset, name, value):
        """
        Gets the queryset with the entered id
        """
        filter_value = {name: value}
        return queryset.filter(**filter_value)

    class Meta:
        model = OrderSerializer.Meta.model
        fields = [
            "user",
        ]
