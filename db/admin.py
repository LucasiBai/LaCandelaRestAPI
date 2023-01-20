from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from db import models


class UserAdmin(BaseUserAdmin):
    """
    User admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "email", "first_name", "last_name"]
    list_display_links = ["email"]

    search_fields = ["id", "email"]

    list_filter = ["is_superuser", "is_active"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        (_("Personal Info"), {"fields": ["first_name", "last_name"]}),
        (_("Permissions"), {"fields": ["is_active", "is_staff", "is_superuser"]}),
        (_("Important Dates"), {"fields": ["last_login"]}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    list_per_page = 10


class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin configuration
    """

    ordering = ["title"]
    list_display = ["title"]
    list_display_links = ["title"]

    search_fields = ["title"]

    list_filter = ["parent__title"]

    fieldsets = ((_("Category Data"), {"fields": ["parent", "title"]}),)

    add_fieldsets = ((None, {"classes": ("wide",), "fields": ["parent", "title"]}),)

    list_per_page = 10


class ProductAdmin(admin.ModelAdmin):
    """
    Product admin configuration
    """

    ordering = ["title"]
    list_display = ["id", "title", "category", "price", "stock"]
    list_display_links = ["title"]

    search_fields = ["id", "title", "category__title"]

    list_filter = ["category__title"]

    fieldsets = (
        (_("Product Public Data"), {"fields": ["title", "description", "price"]}),
        (_("Product Images"), {"fields": ["images"]}),
        (_("Product Meta Data"), {"fields": ["stock", "category", "sold"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": [
                    "title",
                    "description",
                    "price",
                    "images",
                    "stock",
                    "category",
                    "sold",
                ],
            },
        ),
    )

    list_per_page = 10


class CommentAdmin(admin.ModelAdmin):
    """
    Comment admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "user", "product", "rate", "created_at"]
    list_display_links = ["user", "product"]

    search_fields = ["id", "user__email", "product__title", "rate"]

    fieldsets = (
        (_("Comment Public Data"), {"fields": ["subject", "content", "rate"]}),
        (_("Comment References"), {"fields": ["user", "product"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["subject", "content", "rate", "user", "product"],
            },
        ),
    )

    list_per_page = 10


class OrderAdmin(admin.ModelAdmin):
    """
    Order admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "__str__", "created_at"]
    list_display_links = ["__str__"]

    search_fields = [
        "id",
        "buyer__email",
        "shipping_info__address",
        "shipping_info__receiver_dni",
    ]

    fieldsets = (
        (_("Order References"), {"fields": ["buyer", "shipping_info"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["buyer", "shipping_info"],
            },
        ),
    )

    list_per_page = 10


class ShippingInfoAdmin(admin.ModelAdmin):
    """
    Comment admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "__str__", "user"]
    list_display_links = ["__str__"]

    search_fields = ["id", "address", "receiver_dni"]

    fieldsets = (
        (
            _("Shipping Private Data"),
            {"fields": ["address", "receiver", "receiver_dni"]},
        ),
        (_("Shipping References"), {"fields": ["user"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["user", "address", "receiver", "receiver_dni"],
            },
        ),
    )

    list_per_page = 10


class CartAdmin(admin.ModelAdmin):
    """
    Cart admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "__str__", "last_modification"]
    list_display_links = ["__str__"]

    search_fields = ["user__id", "user__email"]

    fieldsets = (
        (_("Cart References"), {"fields": ["user"]}),
        (_("Cart Data"), {"fields": ["total_items"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": [
                    "user",
                ],
            },
        ),
    )

    list_per_page = 10


class CartItemAdmin(admin.ModelAdmin):
    """
    Cart Item admin configuration
    """

    ordering = ["id"]
    list_display = ["id", "cart", "product"]
    list_display_links = ["cart", "product"]

    search_fields = ["cart", "product"]

    fieldsets = (
        (_("Cart Item References"), {"fields": ["cart", "product"]}),
        (_("Cart Item Data"), {"fields": ["count"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["cart", "product", "count"],
            },
        ),
    )

    list_per_page = 10


admin.site.register(models.UserAccount, UserAdmin)  # user admin register
admin.site.register(models.Category, CategoryAdmin)  # category admin register
admin.site.register(models.Product, ProductAdmin)  # product admin register
admin.site.register(models.Comment, CommentAdmin)  # comment admin register
admin.site.register(models.Order, OrderAdmin)  # order admin register
admin.site.register(
    models.ShippingInfo, ShippingInfoAdmin  # shipping info admin register
)
admin.site.register(models.Cart, CartAdmin)  # cart admin register
admin.site.register(models.CartItem, CartItemAdmin)  # cart item admin register
