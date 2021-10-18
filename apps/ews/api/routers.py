from django.urls import path, include
from apps.ews.api.v1 import routers

urlpatterns = [
    path('ews/v1/', include((routers, 'ews_api'), namespace='ews_api')),
]
