from django.urls import path

from .views import CheckoutAPIView, CheckoutNotificationAPIView

urlpatterns = [
    path("checkout/<slug:method>/<int:cart_id>/", CheckoutAPIView.as_view(), name="checkout"),
    path("checkout/notify/<slug:method>/", CheckoutNotificationAPIView.as_view(), name="checkout_notify")
]
