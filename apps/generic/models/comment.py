from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import AbstractCommonField


class AbstractComment(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    description = models.TextField()

    attachments = GenericRelation(
        'generic.Attachment',
        related_query_name='comment'
    )
    reactions = GenericRelation(
        'generic.Reaction',
        related_query_name='comment'
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.description

    @property
    def activity_creator(self):
        return self.activity.user.name


class AbstractCommentTree(AbstractCommonField):
    parent = models.ForeignKey(
        'generic.Comment',
        related_name='parents',
        on_delete=models.CASCADE
    )
    child = models.ForeignKey(
        'generic.Comment',
        related_name='childs',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
