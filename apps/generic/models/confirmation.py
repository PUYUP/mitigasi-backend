from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import AbstractCommonField


class AbstractConfirmation(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='confirmations'
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    # can use number 0 to 100
    # or severe - moderate
    accuracy = models.CharField(max_length=25)
    severity = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    attachments = GenericRelation(
        'generic.Attachment',
        related_query_name='confirmations'
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.accuracy
