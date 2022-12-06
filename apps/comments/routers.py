from rest_framework.routers import DefaultRouter

from .views import CommentViewset

router = DefaultRouter()

router.register(r"comments", CommentViewset)
