from core.loading import is_model_registered
from simple_history.models import HistoricalRecords

from .disaster import *

__all__ = list()


"""DISASTER MODEL"""

if not is_model_registered('ews', 'Disaster'):
    class Disaster(AbstractDisaster):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractDisaster.Meta):
            pass

    __all__.append('Disaster')


if not is_model_registered('ews', 'DisasterLocation'):
    class DisasterLocation(AbstractDisasterLocation):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractDisasterLocation.Meta):
            pass

    __all__.append('DisasterLocation')


if not is_model_registered('ews', 'DisasterVictim'):
    class DisasterVictim(AbstractDisasterVictim):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractDisasterVictim.Meta):
            pass

    __all__.append('DisasterVictim')


if not is_model_registered('ews', 'DisasterDamage'):
    class DisasterDamage(AbstractDisasterDamage):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractDisasterDamage.Meta):
            pass

    __all__.append('DisasterDamage')
