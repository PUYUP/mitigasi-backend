from django.contrib import admin
from apps.eav.forms import BaseDynamicEntityForm
from apps.eav.admin import BaseEntityAdmin

from .models import *


class DisasterLocationInline(admin.StackedInline):
    model = DisasterLocation


class DisasterAdminForm(BaseDynamicEntityForm):
    model = Disaster


class DisasterExtend(BaseEntityAdmin):
    model = Disaster
    inlines = (DisasterLocationInline,)
    form = DisasterAdminForm


admin.site.register(Disaster, DisasterExtend)
admin.site.register(DisasterVictim)
admin.site.register(DisasterDamage)
