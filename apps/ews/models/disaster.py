from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from core.models import AbstractCommonField
from core.constant import (
    DamageClassify,
    DamageLevel,
    DamageMetric,
    DamageVariety,
    VictimAgeGroup,
    VictimGender,
    VictimClassify,
    DisasterIdentifier
)


class AbstractDisaster(AbstractCommonField):
    _Identifier = DisasterIdentifier

    identifier = models.CharField(
        max_length=3,
        choices=_Identifier.choices,
        default=_Identifier.I999,
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    occur_at = models.DateTimeField(db_index=True)
    # from where this disaster info?
    source = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    chronology = models.TextField(null=True, blank=True)

    confirmations = GenericRelation(
        'contribution.Confirmation',
        related_query_name='disaster'
    )
    comments = GenericRelation(
        'contribution.Comment',
        related_query_name='disaster'
    )

    # tracking from where this disaster created
    # for now from :report
    content_type = models.ForeignKey(
        ContentType,
        related_name='disasters',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'ews'
        abstract = True

    def __str__(self) -> str:
        return self.title

    @property
    def location_plain(self):
        locations = [
            loc.locality if loc.locality else loc.sub_administrative_area for loc in self.locations.all()
        ]

        return [loc for loc in locations if loc]


class AbstractDisasterLocation(AbstractCommonField):
    REMOVE_WORDS = ['Desa', 'Kelurahan', 'Kecamatan', 'Kabupaten', 'Provinsi']

    disaster = models.ForeignKey(
        'ews.Disaster',
        related_name='locations',
        on_delete=models.CASCADE
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

    class Meta:
        app_label = 'ews'
        abstract = True

    def __str__(self) -> str:
        return '{}'.format(self.disaster.title)

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


class AbstractDisasterVictim(AbstractCommonField):
    _Gender = VictimGender
    _AgeGroup = VictimAgeGroup
    _Classify = VictimClassify

    disaster = models.OneToOneField(
        'ews.Disaster',
        related_name='victims',
        on_delete=models.CASCADE
    )

    gender = models.CharField(
        max_length=3,
        choices=_Gender.choices,
        default=_Gender.G999
    )
    age_group = models.CharField(
        max_length=3,
        choices=_AgeGroup.choices,
        default=_AgeGroup.AG999
    )
    classify = models.CharField(
        max_length=3,
        choices=_Classify.choices,
        default=_Classify.C999
    )
    amount = models.IntegerField(default=0)

    class Meta:
        app_label = 'ews'
        abstract = True

    def __str__(self) -> str:
        return self.summary

    @property
    def summary(self):
        return '{} {} {} {}'.format(
            self.amount,
            self.get_age_group_display(),
            self.get_gender_display(),
            self.get_classify_display()
        )


class AbstractDisasterDamage(AbstractCommonField):
    _Classify = DamageClassify
    _Variety = DamageVariety
    _Level = DamageLevel
    _Metric = DamageMetric

    disaster = models.OneToOneField(
        'ews.Disaster',
        related_name='damages',
        on_delete=models.CASCADE
    )

    classify = models.CharField(
        max_length=3,
        choices=_Classify.choices,
        default=_Classify.C101
    )
    variety = models.CharField(
        max_length=3,
        choices=_Variety.choices,
        default=_Variety.V999
    )
    level = models.CharField(
        max_length=3,
        choices=_Level.choices,
        default=_Level.L999
    )

    amount = models.IntegerField(default=0)
    metric = models.CharField(
        max_length=3,
        choices=_Metric.choices,
        default=_Metric.M101
    )

    class Meta:
        app_label = 'ews'
        abstract = True

    def __str__(self) -> str:
        return self.summary

    @property
    def summary(self):
        return '{} {} {} {} {}'.format(
            self.amount,
            self.get_metric_display(),
            self.get_classify_display(),
            self.get_variety_display(),
            self.get_level_display()
        )
