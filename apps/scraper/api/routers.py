from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    bmkg_earthquake_feeled_view,
    bmkg_earthquake_recent_view,
    bnpb_dibi_view,
    twitter_bmkg_view,
    ews_bmkg_view
)

urlpatterns = [
    path('scraper/bmkg-earthquake-feeled/', bmkg_earthquake_feeled_view),
    path('scraper/bmkg-earthquake-recent/', bmkg_earthquake_recent_view),
    path('scraper/bnpb-dibi/', bnpb_dibi_view),
    path('scraper/bmkg-twitter/', twitter_bmkg_view),
    path('scraper/bmkg-ews/', ews_bmkg_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
