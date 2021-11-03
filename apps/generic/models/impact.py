from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from core.models import AbstractCommonField, BulkCreateReturnIdManager


class ImpactManager(BulkCreateReturnIdManager, models.Manager):
    pass


class AbstractImpact(AbstractCommonField):
    """
    `impact` based on `location` where `hazard` happend
    this because some `hazard` like `earthquake` has different
    risk each place

    Kedalaman   1       meter
    identifier  value   metric

    III     skala       MMI
    value   idenfier    metric

    15.000  hektar      lahan
    value   metric      identifier

    Jarak pandang   4       meter
    identifier      value   metric

    ---------
    IDE101 + 1 + MET102                 = Kedalaman 1 Meter
    IDE102 + III + MET101               = Skala II MMI
    IDE103 + 5 + MET102                 = Jarak pandang 5 Meter
    IDE104 + 2 + MET104 + Description   = Bangunan 2 unit rusak

    10      unit        bangunan
    value   metric      identifier
    """
    class Metric(models.TextChoices):
        MET101 = '101', _("MMI (Modified Mercalli Intensity)")
        MET102 = '102', _("Meter")
        MET103 = '103', _("Hektar")
        MET104 = '104', _("Unit")

    class Identifier(models.TextChoices):
        IDE101 = '101', _("Kedalaman")
        IDE102 = '102', _("Skala")
        IDE103 = '103', _("Jarak Pandang")
        IDE104 = '104', _("Bangunan")

    metric_display = [
        '<div>%s: %s</div>' % (x.value, x.label) for x in Metric
    ]

    identifier_display = [
        '<div>%s: %s</div>' % (x.value, x.label) for x in Identifier
    ]

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='impacts',
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

    identifier = models.CharField(
        max_length=255,
        help_text=mark_safe(''.join(metric_display)),
        null=True,
        blank=True
    )
    value = models.CharField(max_length=255, null=True, blank=True)
    metric = models.CharField(
        max_length=255,
        help_text=mark_safe(''.join(identifier_display)),
        null=True,
        blank=True
    )
    description = models.TextField(null=True, blank=True)

    objects = ImpactManager()

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.object_id)
