from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import AbstractCommonField


class AbstractActivity(AbstractCommonField):
    """
    Every content from `user` must under `activity`
    such as `comment`.

    Example:
    `content_type` set to `comment`
    `object_id` set to `comment_id`

    Flow:
    1. Create `comment`
    2. Then `Activity.objects.create(content_object=comment)`
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='activities',
        on_delete=models.SET_NULL,
        null=True
    )

    content_type = models.ForeignKey(
        ContentType,
        related_name='activities',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    # <app_label>_<model>
    identifier = models.CharField(max_length=255, editable=False)

    class Meta:
        abstract = True

    @property
    def get_identifier(self):
        return '{}_{}'.format(
            self.content_type.app_label,
            self.content_type.model
        )

    def __str__(self):
        return self.get_identifier

    def save(self, *args, **kwargs):
        self.identifier = self.get_identifier
        super().save(*args, **kwargs)
