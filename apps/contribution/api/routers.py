from django.urls import path, include
from apps.contribution.api.v1 import routers

urlpatterns = [
    path('contribution/v1/', include((routers, 'contribution_api'),
         namespace='contribution_api')),
]
