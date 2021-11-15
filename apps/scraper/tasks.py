from celery import shared_task
from celery.utils.log import get_task_logger

from .target import bmkg_earthquake, bnpb_dibi

logger = get_task_logger(__name__)


@shared_task(name='scraping_bmkg_quake_feeled')
def scraping_bmkg_quake_feeled():
    logger.info('scraping bmkg quake feeled...')
    bmkg_earthquake.quake_feeled()


@shared_task(name='scraping_bmkg_quake_recent')
def scraping_bmkg_quake_recent():
    logger.info('scraping bmkg quake recent...')
    bmkg_earthquake.quake_recent()


@shared_task(name='scraping_bnpb_dibi')
def scraping_bnpb_dibi():
    logger.info('scraping bnpb dibi...')
    bnpb_dibi.dibi()