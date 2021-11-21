from celery import shared_task
from celery.utils.log import get_task_logger

from .target import bmkg_earthquake, bnpb_dibi, bmkg_social_media

logger = get_task_logger(__name__)


@shared_task(name='scraping_bmkg_quake_feeled')
def scraping_bmkg_quake_feeled():
    logger.info('scraping bmkg quake feeled...')
    try:
        bmkg_earthquake.quake_feeled()
    except Exception as e:
        logger.warning(str(e))


@shared_task(name='scraping_bmkg_quake_recent')
def scraping_bmkg_quake_recent():
    logger.info('scraping bmkg quake recent...')
    try:
        bmkg_earthquake.quake_recent()
    except Exception as e:
        logger.warning(str(e))


@shared_task(name='scraping_bnpb_dibi')
def scraping_bnpb_dibi():
    logger.info('scraping bnpb dibi...')
    try:
        bnpb_dibi.dibi()
    except Exception as e:
        logger.warning(str(e))


@shared_task(name='scraping_bmkg_twitter')
def scraping_bmkg_twitter():
    logger.info('scraping bmkg twitter...')
    try:
        bmkg_social_media.twitter()
    except Exception as e:
        logger.warning(str(e))
