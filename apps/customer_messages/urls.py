from django.urls import path

from .views import MessageAPIView

urlpatterns = [
    path("message/<slug:sender>/", MessageAPIView.as_view(), name="message"),
]
