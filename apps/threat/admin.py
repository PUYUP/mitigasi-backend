from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin
from django.apps import apps

from .models import *

Location = apps.get_registered_model('generic', 'Location')
Attachment = apps.get_registered_model('generic', 'Attachment')


"""
Generic
"""


class LocationInline(ct_admin.GenericStackedInline):
    model = Location
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


class AttachmentInline(ct_admin.GenericStackedInline):
    model = Attachment
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


"""
Hazard
"""


class HazardAdmin(admin.ModelAdmin):
    model = Hazard
    inlines = (AttachmentInline, LocationInline,)


admin.site.register(Hazard, HazardAdmin)
admin.site.register(Flood)
admin.site.register(Landslide)
admin.site.register(VolcanicEruption)
admin.site.register(Earthquake)
admin.site.register(Drought)
admin.site.register(Storm)
admin.site.register(Wildfire)
admin.site.register(Tsunami)
admin.site.register(Abrasion)
admin.site.register(Other)
