from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import FilterSet


class FilterMixins:
    """
    Methods for filter queries
    """

    def get_by_id(self, queryset, name, value):
        """
        Gets the queryset with the entered id
        """
        filter_value = {name: value}
        return queryset.filter(**filter_value)

    def query_offset(self, queryset, name, value):
        """
        Gets started item the returned queryset
        """
        return queryset[int(value) - 1:]

    def query_limit(self, queryset, name, value):
        """
        Limits the returned queryset
        """
        return queryset[: int(value)]

    def query_order(self, queryset, name, value):
        """
        Gets query order by ASC or DESC
        """
        if value.upper() == "ASC":
            return queryset.order_by(name)
        elif value.upper() == "DESC":
            return queryset.order_by(f"-{name}")


class FilterResultsFilterset(FilterSet):
    """
    Custom filter methods to get results for filterset
    """

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


class FilterMethodsViewset(ModelViewSet):
    """
    Custom filter methods for Viewsets that have Filterset with 'FilterResults'
    """

    results = 0

    def filter_queryset(self, queryset):
        """
        Gets the filtered queryset and total results from filterset
        """
        for backend in list(self.filter_backends):
            backend_data = backend().filter_queryset(self.request, queryset, self)

            queryset = backend_data["queryset"]

            self.results = backend_data["results"]
        return queryset
