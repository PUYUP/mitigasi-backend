from apps.eav import register
from apps.eav.registry import EavConfig
from .models import *


class DisasterEavConfig(EavConfig):
    generic_relation_related_name = 'eav_disasters'


register(Disaster, DisasterEavConfig)
