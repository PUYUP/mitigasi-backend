from celery.schedules import crontab

import apps.ews.tasks

CELERY_BEAT_SCHEDULE = {
    "sample_task": {
        "task": "apps.ews.tasks.sample_task",
        "schedule": crontab(minute="*/1"),
    },
}
