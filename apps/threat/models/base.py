import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.encoding import smart_str

from apps.generic.helpers import GenericObjSet
from core.models import AbstractCommonField, BulkCreateReturnIdManager
from core.constant import HazardClassify

# Get an instance of a logger
logger = logging.getLogger(__name__)


class HazardManager(BulkCreateReturnIdManager, models.Manager):
    @transaction.atomic
    def create_disaster(self, objs):
        from . import DISASTER_CLASSIFY_MODEL_MAPPER
        disaster_will_create = dict()

        for obj in objs:
            classify = obj.get('classify')
            model = DISASTER_CLASSIFY_MODEL_MAPPER.get(classify)

            if model:
                disaster_obj = model(hazard_id=obj.get('id'))
                disaster_will_create.setdefault(
                    classify, []).append(disaster_obj)

        for classify, value in disaster_will_create.items():
            model = DISASTER_CLASSIFY_MODEL_MAPPER.get(classify)
            if model:
                try:
                    model.objects.bulk_create(value)
                except Exception as e:
                    logger.error(e)

    @transaction.atomic
    def bulk_create_return_with_id(self, *args, **kwargs):
        created_objs = super().bulk_create_return_id(*args, **kwargs)
        self.create_disaster(created_objs)


class AbstractHazard(AbstractCommonField, GenericObjSet):
    _classifies = HazardClassify

    # for scraper this will be empty
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='hazards',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    classify = models.CharField(
        max_length=3,
        choices=_classifies.choices,
        default=_classifies.HAC999,
        db_index=True
    )
    source = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )
    incident = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_("Like `Flood at Perumahan Melati Jaya`")
    )
    occur_at = models.DateTimeField(db_index=True)
    description = models.TextField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    chronology = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        db_index=True
    )

    objects = HazardManager()

    # record all submitted by user with `activity`
    activities = GenericRelation(
        'generic.Activity',
        related_query_name='hazard'
    )

    locations = GenericRelation(
        'generic.Location',
        related_query_name='hazard'
    )
    attachments = GenericRelation(
        'generic.Attachment',
        related_query_name='hazard'
    )
    confirmations = GenericRelation(
        'generic.Confirmation',
        related_query_name='hazard'
    )
    comments = GenericRelation(
        'generic.Comment',
        related_query_name='hazard'
    )
    reactions = GenericRelation(
        'generic.Reaction',
        related_query_name='hazard'
    )
    safetychecks = GenericRelation(
        'generic.SafetyCheck',
        related_query_name='hazard'
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.incident

    @classmethod
    def from_db(cls, db, field_names, values):
        cls._loaded_values = dict(zip(field_names, values))

        instance = super().from_db(db, field_names, values)
        return instance

    @property
    def location_plain(self):
        locations = [
            loc.locality if loc.locality else loc.sub_administrative_area for loc in self.locations.all()
        ]

        return [loc for loc in locations if loc]

    @property
    def activity(self):
        return self.activities.first()

    @property
    def activity_author(self):
        # when this method access set `source` to user name `activity` submitter
        if self.activity:
            name = self.activity.user.name
            if not self.source:
                self.source = name
                self.save(update_fields=('source',))
            return name
        return None

    @property
    def classify_display(self):
        return self.get_classify_display()
