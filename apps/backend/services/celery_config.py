from celery.schedules import crontab
from pytz import timezone


class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0'
    broker_connection_retry_on_startup = True
    CELERY_TIMEZONE = timezone('Europe/London')
    CELERY_BEAT_SCHEDULE = {
        'fetch_data': {
            'task': 'apps.backend.services.tasks.fetch_data',
            'schedule': crontab(minute='*/5')
        },
        'train_tag_predictions': {
            'task': 'apps.backend.services.tasks.train_tag_predictions',
            'schedule': crontab(day_of_month='1'),  # Run once a month, on the first day of the month
        },
    }
