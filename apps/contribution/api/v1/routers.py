from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .report.views import ReportAPIViewSet
from .comment.views import CommentAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('reports', ReportAPIViewSet, basename='report')
router.register('comments', CommentAPIViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
