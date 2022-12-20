from rest_framework.routers import DefaultRouter

from .views import CategoryViewset

router = DefaultRouter()

router.register(r"categories", CategoryViewset, basename="category")
