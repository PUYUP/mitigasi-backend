from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin

from .models import *


class ImpactInline(ct_admin.GenericStackedInline):
    model = Impact
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


class LocationAdmin(admin.ModelAdmin):
    model = Location
    inlines = (ImpactInline,)


admin.site.register(Activity)
admin.site.register(Location, LocationAdmin)
admin.site.register(Attachment)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Confirmation)
admin.site.register(Impact)
