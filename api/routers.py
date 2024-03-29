from django.urls import path, include

from api.views import RootAPIView
from apps.person.api import routers as person_routers
from apps.ews.api import routers as ews_routers
from apps.contribution.api import routers as contribution_routers
from apps.threat.api import routers as threat_routers
from apps.generic.api import routers as generic_routers

urlpatterns = [
    path('', RootAPIView.as_view(), name='api'),
    path('', include(person_routers)),
    path('', include(ews_routers)),
    path('', include(contribution_routers)),
    path('', include(threat_routers)),
    path('', include(generic_routers)),
]
