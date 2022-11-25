from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

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

    fieldsets = ((_("Category Title"), {"fields": ["title"]}),)

    add_fieldsets = ((None, {"classes": ("wide",), "fields": ["title"]}),)

    list_per_page = 10


class ProductAdmin(admin.ModelAdmin):
    """
    Product admin configuration
    """

    ordering = ["title"]
    list_display = ["id", "title", "category", "price", "stock"]
    list_display_links = ["title"]

    search_fields = ["id", "title", "category"]

    list_filter = ["category"]

    fieldsets = (
        (_("Product Public Data"), {"fields": ["title", "description", "price"]}),
        (_("Product Images"), {"fields": ["images"]}),
        (_("Product Meta Data"), {"fields": ["stock", "category", "selled"]}),
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
                    "selled",
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

    search_fields = ["id", "user", "product", "rate"]

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


admin.site.register(models.UserAccount, UserAdmin)  # user admin register
admin.site.register(models.Category, CategoryAdmin)  # category admin register
admin.site.register(models.Product, ProductAdmin)  # product admin register
admin.site.register(models.Comment, CommentAdmin)  # comment admin register
