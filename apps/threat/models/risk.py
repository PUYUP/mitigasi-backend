from decimal import Decimal

from django.db import models
from core.models import AbstractCommonField


# 1
class AbstractFlood(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='flood'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 2
class AbstractLandslide(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='landslide'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 3
class AbstractStorm(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='storm'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 4
class AbstractVolcanicEruption(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='volcaniceruption'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 5
class AbstractDrought(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='drought'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 6
class AbstractEarthquake(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='earthquake'
    )

    depth = models.FloatField(default=Decimal(0.0))
    magnitude = models.FloatField(default=Decimal(0.0))
    latitude = models.FloatField(default=Decimal(0.0), db_index=True)
    longitude = models.FloatField(default=Decimal(0.0), db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 7
class AbstractTsunami(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='tsunami'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 8
class AbstractWildfire(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='wildfire'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 9
class AbstractAbrasion(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='abrasion'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident


# 10
class AbstractOther(AbstractCommonField):
    hazard = models.OneToOneField(
        'threat.Hazard',
        on_delete=models.CASCADE,
        related_name='other'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.hazard.incident
