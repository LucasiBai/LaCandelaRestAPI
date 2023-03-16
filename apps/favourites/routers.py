from rest_framework.routers import DefaultRouter

from .views import FavouriteItemViewset

router = DefaultRouter()

router.register(r"fav-items", FavouriteItemViewset, basename="fav_item")
