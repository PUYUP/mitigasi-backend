from core.loading import is_model_registered

from .location import *

__all__ = list()


if not is_model_registered('territory', 'Provinces'):
    class Provinces(Provinces):
        class Meta(Provinces.Meta):
            pass

    __all__.append('Provinces')


if not is_model_registered('territory', 'Cities'):
    class Cities(Cities):
        class Meta(Cities.Meta):
            pass

    __all__.append('Cities')


if not is_model_registered('territory', 'Districts'):
    class Districts(Districts):
        class Meta(Districts.Meta):
            pass

    __all__.append('Districts')


if not is_model_registered('territory', 'SubDistricts'):
    class SubDistricts(SubDistricts):
        class Meta(SubDistricts.Meta):
            pass

    __all__.append('SubDistricts')
