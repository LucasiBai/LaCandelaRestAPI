from django.utils.translation import gettext_lazy as _
from django.db.models import Q

import django_filters.rest_framework as filters

from .serializers import ProductSerializer
from apps.api_root.utils import FilterMethods


class ProductsFilterSet(filters.FilterSet, FilterMethods):
    """
    Filterset of Product model
    """

    _results = 0

    # Filters

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

    min_rate = filters.NumberFilter(method="query_min_rate", label=_("Min Rate"))
    max_rate = filters.NumberFilter(method="query_max_rate", label=_("Max Rate"))

    offset = filters.NumberFilter(method="query_offset", label=_("Offset"))

    limit = filters.NumberFilter(method="query_limit", label=_("Limit"))

    # Orders

    price_order = filters.CharFilter(
        field_name="price", method="query_order", label=_("Price Order")
    )

    title_order = filters.CharFilter(
        field_name="title", method="query_order", label=_("Title Order")
    )

    # Searcher

    search = filters.CharFilter(method="query_search", label=_("Search Product"))

    def query_search(self, queryset, name, value):
        """
        Search in products by title and description
        """
        return queryset.filter(
            Q(title__icontains=value)
            | Q(description__icontains=value)
            | Q(category__title__icontains=value)
        ).order_by("-sold")

    def get_total_results(self):
        """
        Gets the quantity of total results in request
        """
        return self._results

    def filter_queryset(self, queryset):
        """
        Returns the filtered queryset with total results
        """
        for name, value in self.form.cleaned_data.items():
            if name == "offset":
                self._results = len(queryset)

            queryset = self.filters[name].filter(queryset, value)

        data = {
            "queryset": queryset,
            "results": self.get_total_results(),
        }

        return data

    class Meta:
        model = ProductSerializer.Meta.model
        fields = [
            "title",
            "category",
            "min_price",
            "max_price",
            "title_order",
            "price_order",
            "search",
            "offset",
            "limit",
        ]
