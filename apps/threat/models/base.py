from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import AbstractCommonField, BulkCreateReturnIdManager
from core.constant import HazardClassify


class HazardManager(BulkCreateReturnIdManager, models.Manager):
    @transaction.atomic
    def create_risk(self, objs):
        from . import HAZARD_CLASSIFY_MODEL_MAPPER
        risk_will_create = dict()

        for obj in objs:
            classify = obj.get('classify')
            model = HAZARD_CLASSIFY_MODEL_MAPPER.get(classify)

            if model:
                risk_obj = model(hazard_id=obj.get('id'))
                risk_will_create.setdefault(classify, []).append(risk_obj)

        for classify, value in risk_will_create.items():
            model = HAZARD_CLASSIFY_MODEL_MAPPER.get(classify)
            if model:
                try:
                    model.objects.bulk_create(value)
                except Exception as e:
                    print(e)

    @transaction.atomic
    def bulk_create_return_with_id(self, *args, **kwargs):
        created_objs = super().bulk_create_return_id(*args, **kwargs)
        self.create_risk(created_objs)


class AbstractHazard(AbstractCommonField):
    _classifies = HazardClassify

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
    def author_name(self):
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

    @transaction.atomic
    def set_impacts(self, impacts, locations_obj):
        for index, location in enumerate(locations_obj):
            ct = ContentType.objects.get_for_model(location)
            impact = impacts.get(index, None)
            impacts_obj = list()

            if impact:
                defaults = {
                    'content_type': ct,
                    'object_id': location.id,
                }

                for x in impact:
                    o, _created = location.impacts.get_or_create(
                        defaults=defaults,
                        **x
                    )

                    impacts_obj.append(o)

                if len(impacts_obj) > 0:
                    location.impacts.set(impacts_obj)

    @transaction.atomic
    def set_locations(self, locations):
        locations_obj = list()
        ct = ContentType.objects.get_for_model(self)

        # extract and remove `impacts` from `locations`
        impacts = {
            i: v for i, v in enumerate([o.pop('impacts', None) for o in locations])
        }

        defaults = {
            'content_type': ct,
            'object_id': self.id,
        }

        for data in locations:
            o, _create = self.locations.update_or_create(
                defaults=defaults,
                **data
            )

            locations_obj.append(o)

        # `impacts` created after `locations` created
        self.set_impacts(impacts, locations_obj)

        # set `locations` to instance
        self.locations.set(locations_obj)
