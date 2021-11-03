import os

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import AbstractCommonField


class AbstractAttachment(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

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

    activities = GenericRelation(
        'generic.Activity',
        related_query_name='attachment'
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)

        if self.file:
            self.filesize = self.file.size

        super().save(*args, **kwargs)
