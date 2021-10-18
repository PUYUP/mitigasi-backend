from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from apps.eav.admin import BaseEntityAdmin
from apps.eav.forms import BaseDynamicEntityForm

from .models import *


class AttachmentInline(GenericStackedInline):
    model = Attachment


class ReportLocationInline(admin.StackedInline):
    model = ReportLocation


class ReportAdminForm(BaseDynamicEntityForm):
    model = Report


class ReportExtend(BaseEntityAdmin):
    model = Report
    inlines = (ReportLocationInline, AttachmentInline,)
    form = ReportAdminForm


class CommentExtend(admin.ModelAdmin):
    model = Comment
    inlines = (AttachmentInline,)


admin.site.register(Activity)
admin.site.register(Report, ReportExtend)
admin.site.register(Comment, CommentExtend)
admin.site.register(CommentTree)
admin.site.register(Confirmation)
admin.site.register(Attachment)
admin.site.register(Reaction)
