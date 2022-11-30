from .serializers import Comment


def get_validated_rate_products_pk(filter, queryset, value):
    """
    Returns a list of pks greater or lower than ingresed value
    """

    validated_id_products = []

    for instance in queryset:
        comments_of_product = Comment.objects.filter(product=instance)

        if comments_of_product:
            rate = round(
                sum(comment.rate for comment in comments_of_product)
                / len(comments_of_product),
                2,
            )
        else:
            rate = 5.00

        if filter == "gte":
            if rate >= value:
                validated_id_products.append(instance.id)
        elif filter == "lte":
            if rate <= value:
                validated_id_products.append(instance.id)
        else:
            raise ValueError("Filter must be 'gte' or 'lte'")

    return validated_id_products
