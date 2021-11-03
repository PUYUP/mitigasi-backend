from core.loading import is_model_registered
from simple_history.models import HistoricalRecords

from .disaster import *

__all__ = list()


"""DISASTER MODEL"""

if not is_model_registered('ews', 'Disaster'):
    class Disaster(AbstractDisaster):
        class Meta(AbstractDisaster.Meta):
            pass

    __all__.append('Disaster')


if not is_model_registered('ews', 'DisasterLocation'):
    class DisasterLocation(AbstractDisasterLocation):
        class Meta(AbstractDisasterLocation.Meta):
            pass

    __all__.append('DisasterLocation')


if not is_model_registered('ews', 'DisasterVictim'):
    class DisasterVictim(AbstractDisasterVictim):
        class Meta(AbstractDisasterVictim.Meta):
            pass

    __all__.append('DisasterVictim')


if not is_model_registered('ews', 'DisasterDamage'):
    class DisasterDamage(AbstractDisasterDamage):
        class Meta(AbstractDisasterDamage.Meta):
            pass

    __all__.append('DisasterDamage')


if not is_model_registered('ews', 'DisasterAttachment'):
    class DisasterAttachment(AbstractDisasterAttachment):
        class Meta(AbstractDisasterAttachment.Meta):
            pass

    __all__.append('DisasterAttachment')
