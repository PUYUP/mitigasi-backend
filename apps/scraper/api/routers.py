from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import bmkg_earthquake_feeled, bmkg_earthquake_recent, bnpb_dibi

urlpatterns = [
    path('scraper/bmkg-earthquake-feeled/', bmkg_earthquake_feeled),
    path('scraper/bmkg-earthquake-recent/', bmkg_earthquake_recent),
    path('scraper/bnpb-dibi/', bnpb_dibi),
]

urlpatterns = format_suffix_patterns(urlpatterns)
