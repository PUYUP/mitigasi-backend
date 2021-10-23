from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(name='scraping_bnpb_dipi')
def scraping_bnpb_dipi():
    print('scraping bnpb dipi...')
