from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls", namespace="users")),
    path("api/", include("apps.products.urls", namespace="products")),
]
