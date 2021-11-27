from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('mitigasi')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
#   https://docs.celeryproject.org/en/stable/userguide/application.html
app.config_from_object('config.settings.celeryconfig', namespace='CELERY')

# Load task modules from all registered Django app configs.
# Auto-find task.py in each apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


"""
# temporary disabled to many data not necessary
app.conf.beat_schedule = {
    # Scheduler Name
    'scraping-bnbp-dibi-each-4-hours': {
        'task': 'scraping_bnpb_dibi',
        'schedule': crontab(minute=0, hour='*/4'),
    },

    'scraping-bmkg-quake-feeled-each-20-minutes': {
        'task': 'scraping_bmkg_quake_feeled',
        'schedule': crontab(minute='*/20'),
    },

    'scraping-bmkg-quake-recent-each-10-minutes': {
        'task': 'scraping_bmkg_quake_recent',
        'schedule': crontab(minute='*/10'),
    },

    'scraping-bmkg-twitter-each-20-minutes': {
        'task': 'scraping_bmkg_twitter',
        'schedule': crontab(minute='*/10'),
    },
}
"""

if __name__ == '__main__':
    app.start()
