from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.contenttypes.models import ContentType

from core.constant import ReactionIdentifier
from core.models import AbstractCommonField


class AbstractReaction(AbstractCommonField):
    _identifier = ReactionIdentifier

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    identifier = models.CharField(
        max_length=15,
        choices=_identifier.choices,
        default=_identifier.REI101
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.get_identifier_display()
