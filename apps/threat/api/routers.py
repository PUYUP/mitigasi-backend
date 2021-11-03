from django.urls import path, include
from apps.threat.api.v1 import routers

urlpatterns = [
    path('threat/v1/', include((routers, 'threat_api'), namespace='threat_api')),
]
