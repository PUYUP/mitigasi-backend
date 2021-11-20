from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import bmkg_earthquake_feeled, bmkg_earthquake_recent, bnpb_dibi, twitter_bmkg

urlpatterns = [
    path('scraper/bmkg-earthquake-feeled/', bmkg_earthquake_feeled),
    path('scraper/bmkg-earthquake-recent/', bmkg_earthquake_recent),
    path('scraper/bnpb-dibi/', bnpb_dibi),
    path('scraper/bmkg-twitter/', twitter_bmkg),
]

urlpatterns = format_suffix_patterns(urlpatterns)
