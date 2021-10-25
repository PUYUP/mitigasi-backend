import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from core.constant import ReactionIdentifier

from core.models import AbstractCommonField


class AbstractConfirmation(AbstractCommonField):
    activity = models.ForeignKey(
        'contribution.Activity',
        related_name='confirmations',
        on_delete=models.CASCADE
    )

    # targeted parent model
    # ex; :disaster, :report
    content_type = models.ForeignKey(
        ContentType,
        related_name='confirmations',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    # can use number 0 to 100
    # or severe - moderate
    accuracy = models.CharField(max_length=15)
    severity = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    necessary = models.TextField(null=True, blank=True)
    attachments = GenericRelation(
        'contribution.Attachment',
        related_query_name='confirmations'
    )

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return self.get_vote_display()


class AbstractReaction(AbstractCommonField):
    _Identifier = ReactionIdentifier

    activity = models.ForeignKey(
        'contribution.Activity',
        related_name='reactions',
        on_delete=models.CASCADE
    )

    # targeted parent model
    # ex; :disaster, :report
    content_type = models.ForeignKey(
        ContentType,
        related_name='reactions',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    identifier = models.CharField(
        max_length=15,
        choices=_Identifier.choices,
        default=_Identifier.RI101
    )

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return self.get_identifier_display()


class AbstractComment(AbstractCommonField):
    activity = models.ForeignKey(
        'contribution.Activity',
        related_name='comments',
        on_delete=models.CASCADE
    )

    # targeted parent model
    # ex; :disaster, :report
    content_type = models.ForeignKey(
        ContentType,
        related_name='comments',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    description = models.TextField()
    attachments = GenericRelation(
        'contribution.Attachment',
        related_query_name='comments'
    )

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return self.description

    @property
    def activity_creator(self):
        return self.activity.user.name


class AbstractCommentTree(AbstractCommonField):
    parent = models.ForeignKey(
        'contribution.Comment',
        related_name='parents',
        on_delete=models.CASCADE
    )
    child = models.ForeignKey(
        'contribution.Comment',
        related_name='childs',
        on_delete=models.CASCADE
    )

    class Meta:
        app_label = 'contribution'
        abstract = True


class AbstractAttachment(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        related_name='attachments',
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(
        upload_to='attachment/%Y/%m/%d',
        null=True,
        blank=True
    )
    filename = models.CharField(
        max_length=255,
        editable=False,
        null=True,
        blank=True
    )
    filepath = models.CharField(
        max_length=255,
        editable=False,
        null=True,
        blank=True
    )
    filesize = models.IntegerField(
        editable=False,
        null=True,
        blank=True
    )
    filemime = models.CharField(
        max_length=255,
        editable=False,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    caption = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)

        self.filesize = self.file.size
        super().save(*args, **kwargs)
