from core.loading import is_model_registered

from .location import *

__all__ = list()


if not is_model_registered('territory', 'Provinces'):
    class Provinces(AbstractProvinces):
        class Meta(AbstractProvinces.Meta):
            pass

    __all__.append('Provinces')


if not is_model_registered('territory', 'Cities'):
    class Cities(AbstractCities):
        class Meta(AbstractCities.Meta):
            pass

    __all__.append('Cities')


if not is_model_registered('territory', 'Districts'):
    class Districts(AbstractDistricts):
        class Meta(AbstractDistricts.Meta):
            pass

    __all__.append('Districts')


if not is_model_registered('territory', 'SubDistricts'):
    class SubDistricts(AbstractSubDistricts):
        class Meta(AbstractSubDistricts.Meta):
            pass

    __all__.append('SubDistricts')
