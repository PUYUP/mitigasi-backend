from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.contribution.conf import settings
from core.models import AbstractCommonField


class AbstractActivity(AbstractCommonField):
    """
    General purpose of :activity
    can use for :comment, :confirmation, others

    Example;
    User :report a disaster so :content_type must set to :disaster
    with :object_id set to null/empty then user complete their report
    in :report model

    Now has
    - :confirmation
    - :comment
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
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # <app_label>_<model>
    identifier = models.CharField(max_length=255, editable=False)

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self):
        return self.identifier

    def save(self, *args, **kwargs):
        self.identifier = '{}_{}'.format(
            self.content_type.app_label,
            self.content_type.model
        )
        super().save(*args, **kwargs)
