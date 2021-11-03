from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .hazard.views import HazardAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('hazards', HazardAPIViewSet, basename='hazard')

urlpatterns = [
    path('', include(router.urls)),
]
