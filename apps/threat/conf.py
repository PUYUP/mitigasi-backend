# https://pypi.org/project/django-appconf/
from django.conf import settings  # noqa
from appconf import AppConf


class ThreatAppConf(AppConf):
    class Meta:
        perefix = 'threat'
