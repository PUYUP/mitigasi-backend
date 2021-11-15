from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin
from django.contrib.contenttypes.models import ContentType

from .models import *


class ImpactInline(ct_admin.GenericStackedInline):
    model = Impact
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


class LocationAdmin(admin.ModelAdmin):
    model = Location
    inlines = (ImpactInline,)


class ContentTypeAdmin(admin.ModelAdmin):
    model = ContentType
    search_fields = ('model',)


"""
Comment
"""


class CommentTreeParentInline(admin.StackedInline):
    model = CommentTree
    fk_name = 'child'


class CommentTreeChildInline(admin.StackedInline):
    model = CommentTree
    fk_name = 'parent'


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    inlines = (CommentTreeParentInline, CommentTreeChildInline,)


"""
SafetyCheck
"""


class LocationInline(ct_admin.GenericStackedInline):
    model = Location
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


class AttachmentInline(ct_admin.GenericStackedInline):
    model = Attachment
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


class SafetyCheckAdmin(admin.ModelAdmin):
    model = SafetyCheck
    inlines = (AttachmentInline, LocationInline,)


admin.site.register(ContentType, ContentTypeAdmin)
admin.site.register(Activity)
admin.site.register(Location, LocationAdmin)
admin.site.register(Attachment)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reaction)
admin.site.register(Confirmation)
admin.site.register(Impact)
admin.site.register(SafetyCheck, SafetyCheckAdmin)
