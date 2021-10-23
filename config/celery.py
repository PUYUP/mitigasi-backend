import os

from __future__ import absolute_import, unicode_literals
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


app.conf.beat_schedule = {
    # Scheduler Name
    'scraping-bnbp-dipi-five-seconds': {
        # Task Name (Name Specified in Decorator)
        'task': 'scraping_bnpb_dipi',
        # Schedule
        'schedule': crontab(minute=0, hour='*/1'),
    },
}


if __name__ == '__main__':
    app.start()
