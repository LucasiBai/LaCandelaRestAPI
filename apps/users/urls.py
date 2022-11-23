from django.urls import path

from .routers import router
from .views.token_views import LoginTokenObtainView, LoginTokenRefreshView
from .views.apiview_views import ResetPasswordApiView, ChangePasswordConfirmApiView


app_name = "users"

urlpatterns = [
    path("login/", LoginTokenObtainView.as_view(), name="user_token_obtain"),
    path("login/refresh/", LoginTokenRefreshView.as_view(), name="user_token_refresh"),
    path("reset-password/", ResetPasswordApiView.as_view(), name="reset_password"),
    path(
        "reset-password/<str:encoded_pk>/<str:token>/",
        ChangePasswordConfirmApiView.as_view(),
        name="reset_password-confirm",
    ),
]

urlpatterns += router.urls
