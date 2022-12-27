from rest_framework.routers import DefaultRouter

from .views.viewset_views import ProductsViewSet

router = DefaultRouter()

router.register(r"products", ProductsViewSet)
