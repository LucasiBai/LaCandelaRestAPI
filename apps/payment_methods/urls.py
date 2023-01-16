from django.urls import path

from .views import CheckoutAPIView

urlpatterns = [
    path("checkout/<slug:method>/<int:cart_id>/", CheckoutAPIView.as_view(), name="checkout")
]
