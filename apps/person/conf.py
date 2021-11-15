# https://pypi.org/project/django-appconf/
from django.conf import settings  # noqa
from appconf import AppConf


class PersonAppConf(AppConf):
    # use `msisdn` or `email` or both
    # if empty verification at register not required
    VERIFICATION_FIELDS = []

    class Meta:
        perefix = 'person'
