from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .scraper.views import BMKG_TEWS_Realtime_ScraperAPIView, BMKG_TEWS_Recent_ScraperAPIView, BMKG_TEWS_ScraperAPIView, BNPB_DIBI_ScraperAPIView
from .disaster.views import DisasterAPIViewSet

router = DefaultRouter(trailing_slash=True)
router.register('disasters', DisasterAPIViewSet, basename='disaster')

urlpatterns = [
    path('', include(router.urls)),
    path('scraper/bnbp-dipi/', BNPB_DIBI_ScraperAPIView.as_view(),
         name='scraper-bnpb-dipi'),
    path('scraper/bmkg-tews/', BMKG_TEWS_ScraperAPIView.as_view(),
         name='scraper-bmkg-tews'),
    path('scraper/bmkg-tews-recent/', BMKG_TEWS_Recent_ScraperAPIView.as_view(),
         name='scraper-bmkg-tews-recent'),
    path('scraper/bmkg-tews-realtime/', BMKG_TEWS_Realtime_ScraperAPIView.as_view(),
         name='scraper-bmkg-tews-realtime'),
]
