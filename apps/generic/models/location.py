from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import AbstractCommonField, BulkCreateReturnIdManager

REMOVED_TERMS = [
    'Desa',
    'Kelurahan',
    'Kecamatan',
    'Kabupaten',
    'Provinsi'
]


class LocationManager(BulkCreateReturnIdManager, models.Manager):
    pass


class AbstractLocation(AbstractCommonField):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='locations',
        null=True,
        blank=True
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    country = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )
    country_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    # province
    administrative_area = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )
    administrative_area_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    # city
    sub_administrative_area = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )
    sub_administrative_area_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    # district
    locality = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )
    locality_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    # village
    sub_locality = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )
    sub_locality_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    thoroughfare = models.CharField(
        null=True,
        blank=True,
        max_length=255
    )
    sub_thoroughfare = models.CharField(
        null=True,
        blank=True,
        max_length=255
    )

    areas_of_interest = models.TextField(
        null=True,
        blank=True,
        max_length=255,
        help_text=_("Separate by ;")
    )
    postal_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True
    )

    latitude = models.FloatField(default=Decimal(0.0), db_index=True)
    longitude = models.FloatField(default=Decimal(0.0), db_index=True)

    impacts = GenericRelation('generic.Impact', related_query_name='location')
    objects = LocationManager()

    class Meta:
        app_label = 'generic'
        abstract = True

    def __str__(self) -> str:
        return '{}, {}'.format(self.latitude, self.longitude)

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean_terms()
        super().save(*args, **kwargs)

    def clean_terms(self):
        for r in REMOVED_TERMS:
            if self.administrative_area:
                self.administrative_area = self.administrative_area \
                    .replace(r, '').strip()

            if self.sub_administrative_area:
                self.sub_administrative_area = self.sub_administrative_area \
                    .replace(r, '').strip()

            if self.locality:
                self.locality = self.locality.replace(r, '').strip()

            if self.sub_locality:
                self.sub_locality = self.sub_locality.replace(r, '').strip()
