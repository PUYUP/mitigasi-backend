from core.loading import is_model_registered
from simple_history.models import HistoricalRecords

from .notification import *

__all__ = list()


# 1
if not is_model_registered('notifier', 'Notification'):
    class Notification(AbstractNotification):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractNotification.Meta):
            pass

    __all__.append('Notification')
