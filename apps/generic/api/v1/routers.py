from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .attachment.views import AttachmentAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('attachments', AttachmentAPIViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]
