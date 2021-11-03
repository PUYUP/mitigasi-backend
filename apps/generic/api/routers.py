from django.urls import path, include
from apps.generic.api.v1 import routers

urlpatterns = [
    path('generic/v1/', include((routers, 'generic_api'), namespace='generic_api')),
]
