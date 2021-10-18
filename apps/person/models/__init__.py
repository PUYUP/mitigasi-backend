from apps.eav import register
from apps.eav.registry import EavConfig

from .models import *


class UserEavConfig(EavConfig):
    generic_relation_related_name = 'eav_users'


class ProfileEavConfig(EavConfig):
    generic_relation_related_name = 'eav_profiles'


register(Profile, ProfileEavConfig)
