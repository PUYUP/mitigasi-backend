from core.loading import is_model_registered

from .base import *
from .disaster import *

__all__ = list()


if not is_model_registered('threat', 'Hazard'):
    class Hazard(AbstractHazard):
        class Meta(AbstractHazard.Meta):
            pass

    __all__.append('Hazard')


if not is_model_registered('threat', 'Flood'):
    class Flood(AbstractFlood):
        class Meta(AbstractFlood.Meta):
            pass

    __all__.append('Flood')


if not is_model_registered('threat', 'Landslide'):
    class Landslide(AbstractLandslide):
        class Meta(AbstractLandslide.Meta):
            pass

    __all__.append('Landslide')


if not is_model_registered('threat', 'Storm'):
    class Storm(AbstractStorm):
        class Meta(AbstractStorm.Meta):
            pass

    __all__.append('Storm')


if not is_model_registered('threat', 'VolcanicEruption'):
    class VolcanicEruption(AbstractVolcanicEruption):
        class Meta(AbstractVolcanicEruption.Meta):
            pass

    __all__.append('VolcanicEruption')


if not is_model_registered('threat', 'Drought'):
    class Drought(AbstractDrought):
        class Meta(AbstractDrought.Meta):
            pass

    __all__.append('Drought')


if not is_model_registered('threat', 'Earthquake'):
    class Earthquake(AbstractEarthquake):
        class Meta(AbstractEarthquake.Meta):
            pass

    __all__.append('Earthquake')


if not is_model_registered('threat', 'Tsunami'):
    class Tsunami(AbstractTsunami):
        class Meta(AbstractTsunami.Meta):
            pass

    __all__.append('Tsunami')


if not is_model_registered('threat', 'Wildfire'):
    class Wildfire(AbstractWildfire):
        class Meta(AbstractWildfire.Meta):
            pass

    __all__.append('Wildfire')


if not is_model_registered('threat', 'Abrasion'):
    class Abrasion(AbstractAbrasion):
        class Meta(AbstractAbrasion.Meta):
            pass

    __all__.append('Abrasion')


if not is_model_registered('threat', 'Other'):
    class Other(AbstractOther):
        class Meta(AbstractOther.Meta):
            pass

    __all__.append('Other')
