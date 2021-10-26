from eav import register
from eav.registry import EavConfig
from .models import *


class DisasterEavConfig(EavConfig):
    manager_attr = 'objects'
    generic_relation_attr = 'eav_values'
    generic_relation_related_name = 'disasters'


register(Disaster, DisasterEavConfig)
