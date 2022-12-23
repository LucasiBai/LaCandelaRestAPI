from apps.products.utils import get_validated_rate_products_pk


class FilterMethods:
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
        return queryset[value - 1 :]

    def query_limit(self, queryset, name, value):
        """
        Limits the returned queryset
        """
        return queryset[:value]

    def query_min_rate(self, queryset, name, value):
        """
        Gets the returned products greater or equal than value
        """

        validated_id_products = get_validated_rate_products_pk("gte", queryset, value)

        return queryset.filter(pk__in=validated_id_products)

    def query_max_rate(self, queryset, name, value):
        """
        Gets the returned products lower or equal than value
        """
        validated_id_products = get_validated_rate_products_pk("lte", queryset, value)

        return queryset.filter(pk__in=validated_id_products)

    def query_order(self, queryset, name, value):
        """
        Gets query order by ASC or DESC
        """
        if value.upper() == "ASC":
            return queryset.order_by(name)
        elif value.upper() == "DESC":
            return queryset.order_by(f"-{name}")
