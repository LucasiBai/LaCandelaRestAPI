from django.urls import path

from .views import CartApiView, CartItemRetrieveApiView

urlpatterns = [
    path("cart/", CartApiView.as_view(), name="my-cart"),
    path("cart/<int:pk>/", CartItemRetrieveApiView.as_view(), name="cart_item"),
]
