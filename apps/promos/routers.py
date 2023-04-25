from rest_framework.routers import DefaultRouter

from .views import PromoAPIViewset

router = DefaultRouter()

router.register(r"promos", PromoAPIViewset)
