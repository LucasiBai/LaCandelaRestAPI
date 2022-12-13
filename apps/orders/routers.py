from rest_framework.routers import DefaultRouter

from .views import OrderViewset

router = DefaultRouter()

router.register(r"orders", OrderViewset)
