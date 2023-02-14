from rest_framework.routers import DefaultRouter

from .views import ShippingInfoViewset

router = DefaultRouter()

router.register(r"shipping_info", ShippingInfoViewset, basename="shipping_info")
