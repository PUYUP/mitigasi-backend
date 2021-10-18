# https://pypi.org/project/django-appconf/
from django.conf import settings  # noqa
from appconf import AppConf


class ContributionAppConf(AppConf):
    class Meta:
        perefix = 'contribution'
