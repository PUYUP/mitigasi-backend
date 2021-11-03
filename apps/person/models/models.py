from simple_history.models import HistoricalRecords

from ..utils import is_model_registered
from .user import *
from .securecode import *

__all__ = list()


# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#auth-custom-user
if not is_model_registered('person', 'User'):
    class User(User):
        class Meta(User.Meta):
            pass

    __all__.append('User')


if not is_model_registered('person', 'Profile'):
    class Profile(AbstractProfile):
        class Meta(AbstractProfile.Meta):
            pass

    __all__.append('Profile')


if not is_model_registered('person', 'SecureCode'):
    class SecureCode(AbstractSecureCode):
        class Meta(AbstractSecureCode.Meta):
            pass

    __all__.append('SecureCode')
