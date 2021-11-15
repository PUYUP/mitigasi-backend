from django.urls import path, include

from api.views import RootAPIView
from apps.person.api import routers as person_routers
from apps.threat.api import routers as threat_routers
from apps.generic.api import routers as generic_routers
from apps.scraper.api import routers as scraper_routers

urlpatterns = [
    path('', RootAPIView.as_view(), name='api'),
    path('', include(person_routers)),
    path('', include(threat_routers)),
    path('', include(generic_routers)),
    path('', include(scraper_routers)),
]
