from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.conf import settings

from core.models import AbstractCommonField


class AbstractComment(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.TextField()

    activities = GenericRelation(
        'generic.Activity',
        related_query_name='comment'
    )
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
    def activity(self):
        return self.activities \
            .prefetch_related('user', 'content_type') \
            .select_related('user', 'content_type') \
            .first()

    @property
    def activity_author(self):
        if not self.user and self.activity:
            self.user = self.activity.user
            self.save(update_fields=('user',))

            return self.activity.user.name
        return self.user.name

    @property
    def parent(self):
        if hasattr(self, 'child'):
            return self.child.parent
        return None

    @transaction.atomic
    def save(self, *args, **kwargs):
        if hasattr(self.content_object, 'user') and not self.pk:
            self.user = self.content_object.user

        super().save(*args, **kwargs)


class AbstractCommentTree(AbstractCommonField):
    parent = models.ForeignKey(
        'generic.Comment',
        related_name='parents',
        on_delete=models.CASCADE
    )
    child = models.OneToOneField(
        'generic.Comment',
        related_name='child',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
