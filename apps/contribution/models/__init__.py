from apps.eav import register
from apps.eav.registry import EavConfig

from .models import *


class ReportEavConfig(EavConfig):
    generic_relation_related_name = 'eav_reports'


register(Report, ReportEavConfig)
