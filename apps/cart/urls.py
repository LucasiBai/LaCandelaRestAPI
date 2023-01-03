from django.urls import path

from .views import CartApiView

urlpatterns = [path("cart/", CartApiView.as_view(), name="my-cart")]
