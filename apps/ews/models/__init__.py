from eav import register
from eav.registry import EavConfig
from .models import *


class DisasterEavConfig(EavConfig):
    manager_attr = 'eav_objects'
    generic_relation_attr = 'disasters_eav_values'
    generic_relation_related_name = 'disasters'


register(Disaster, DisasterEavConfig)
