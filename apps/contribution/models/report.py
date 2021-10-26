from decimal import Decimal
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import AbstractCommonField
from core.constant import ConfirmationReaction, DisasterIdentifier


class AbstractReport(AbstractCommonField):
    """:report will up as :disaster after raised X confirmation"""
    _Identifier = DisasterIdentifier

    activity = models.ForeignKey(
        'contribution.Activity',
        related_name='reports',
        on_delete=models.CASCADE
    )

    identifier = models.CharField(
        max_length=3,
        choices=_Identifier.choices,
        default=_Identifier.DIS999,
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    occur_at = models.DateTimeField(db_index=True)
    # from where this report source?
    source = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    chronology = models.TextField(null=True, blank=True)
    necessary = models.TextField(null=True, blank=True)

    confirmations = GenericRelation(
        'contribution.Confirmation',
        related_query_name='report'
    )
    comments = GenericRelation(
        'contribution.Comment',
        related_query_name='report'
    )
    attachments = GenericRelation(
        'contribution.Attachment',
        related_query_name='report'
    )

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return self.title

    @property
    def location_plain(self):
        locations = [
            self.location.locality if self.location.locality else self.location.sub_administrative_area
        ]

        return [loc for loc in locations if loc]

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.source:
            self.source = self.activity.user.name

        super().save(*args, **kwargs)

    def create_disaster(self):
        if self.confirmations.filter(vote=ConfirmationReaction.CV101).count() >= 1:
            report_model_name = self._meta.model._meta.model_name
            ctype = ContentType.objects.get(model=report_model_name)
            Disaster = apps.get_registered_model('ews', 'Disaster')
            Location = apps.get_registered_model('ews', 'DisasterLocation')

            # create disaster
            disaster_obj = Disaster.objects.create(
                identifier=self.identifier,
                title=self.title,
                datetime=self.datetime,
                source=self.source,
                description=self.description,
                reason=self.reason,
                chronology=self.chronology,
                content_type=ctype,
                object_id=self.id
            )

            Location.objects.create(
                disaster=disaster_obj,

                latitude=self.location.latitude,
                longitude=self.location.longitude,

                country=self.location.country,
                country_code=self.location.country_code,

                administrative_area=self.location.administrative_area,
                administrative_area_code=self.location.administrative_area_code,

                sub_administrative_area=self.location.sub_administrative_area,
                sub_administrative_area_code=self.location.sub_administrative_area_code,

                locality=self.location.locality,
                locality_code=self.location.locality_code,

                sub_locality=self.location.sub_locality,
                sub_locality_code=self.location.sub_locality_code,

                thoroughfare=self.location.thoroughfare,
                sub_thoroughfare=self.sub_thoroughfare,
                postal_code=self.location.postal_code,
            )

            return disaster_obj


class AbstractReportLocation(AbstractCommonField):
    REMOVE_WORDS = ['Desa', 'Kelurahan', 'Kecamatan', 'Kabupaten', 'Provinsi']

    report = models.OneToOneField(
        'contribution.Report',
        related_name='location',
        on_delete=models.CASCADE
    )

    severity = models.CharField(max_length=255, null=True, blank=True)

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

    class Meta:
        app_label = 'contribution'
        abstract = True

    def __str__(self) -> str:
        return '{}'.format(self.report.title)

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean_words()
        super().save(*args, **kwargs)

    def clean_words(self):
        for r in self.REMOVE_WORDS:
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
