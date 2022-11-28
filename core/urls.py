from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api_root.urls", namespace="api")),
    path("api/users/", include("apps.users.urls", namespace="users")),
]
