from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .scraper.views import BNPB_DIBI_ScraperAPIView
from .disaster.views import DisasterAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('disasters', DisasterAPIViewSet, basename='disaster')

urlpatterns = [
    path('', include(router.urls)),
    path('scraper/bnbp-dipi/', BNPB_DIBI_ScraperAPIView.as_view(),
         name='scraper-bnpb-dipi'),
]
