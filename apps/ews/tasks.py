from celery import shared_task
from celery.utils.log import get_task_logger

from .scraper.bnpb import dibi
from .scraper.bmkg import quake, quake_realtime, quake_recent

logger = get_task_logger(__name__)


@shared_task(name='scraping_bnpb_dipi')
def scraping_bnpb_dipi():
    logger.info('scraping bnpb dipi...')

    scrape = dibi()
    if scrape is None:
        logger.info('has data...')
    logger.info('no data...')


@shared_task(name='scraping_bmkg_quake')
def scraping_bmkg_quake():
    logger.info('scraping bmkg quake...')
    quake()


@shared_task(name='scraping_bmkg_quake_recent')
def scraping_bmkg_quake_recent():
    logger.info('scraping bmkg quake recent...')
    quake_recent()


@shared_task(name='scraping_bmkg_quake_realtime')
def scraping_bmkg_quake_realtime():
    logger.info('scraping bmkg quake realtime...')
    quake_realtime()
