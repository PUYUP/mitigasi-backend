# https://pypi.org/project/django-appconf/
from django.conf import settings  # noqa
from appconf import AppConf


class NotifierAppConf(AppConf):
    SOFT_DELETE = False

    class Meta:
        perefix = 'notifier'
