from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .attachment.views import AttachmentAPIViewSet
from .activity.views import ActivityAPIViewSet
from .comment.views import CommentAPIViewSet
from .safetycheck.views import SafetyCheckAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('attachments', AttachmentAPIViewSet, basename='attachment')
router.register('activities', ActivityAPIViewSet, basename='activity')
router.register('comments', CommentAPIViewSet, basename='comment')
router.register('safetychecks', SafetyCheckAPIViewSet, basename='safetycheck')

urlpatterns = [
    path('', include(router.urls)),
]
