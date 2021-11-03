from .models import *

HAZARD_CLASSIFY_MODEL_MAPPER = {
    '101': Flood,
    '102': Storm,
    '103': Landslide,
    '104': Wildfire,
    '105': Earthquake,
    '106': Abrasion,
    '107': Drought,
    '108': Tsunami,
    '109': VolcanicEruption,
    '999': Other,
}
