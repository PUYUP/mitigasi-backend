from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.generic.helpers import GenericObjSet

from core.models import AbstractCommonField


class AbstractSafetyCheck(AbstractCommonField, GenericObjSet):
    class Condition(models.TextChoices):
        AFFECTED = 'affected', _("Affected")
        SAFE = 'safe', _("Safe")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='safetychecks',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    content_type = models.ForeignKey(
        ContentType,
        related_name='safetychecks',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    condition = models.CharField(
        choices=Condition.choices,
        max_length=15,
        db_index=True
    )
    situation = models.TextField(null=True, blank=True)

    activities = GenericRelation(
        'generic.Activity',
        related_query_name='safetycheck'
    )
    locations = GenericRelation(
        'generic.Location',
        related_query_name='safetycheck'
    )
    attachments = GenericRelation(
        'generic.Attachment',
        related_query_name='safetycheck'
    )
    comments = GenericRelation(
        'generic.Comment',
        related_query_name='safetycheck'
    )
    reactions = GenericRelation(
        'generic.Reaction',
        related_query_name='safetycheck'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_condition_display()

    @property
    def activity_author(self):
        if not self.user and self.activity:
            self.user = self.activity.user
            self.save(update_fields=('user',))

            return self.activity.user.name
        return self.user.name

    def check_have_confirmed_or_not(self):
        if self.__class__.objects \
                .filter(
                    user=self.user,
                    content_type=self.content_type,
                    object_id=self.object_id
                ).exists():

            raise ValidationError({'user': _("You have confirmed this")})
