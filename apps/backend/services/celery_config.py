from celery.schedules import crontab


class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0'
    broker_connection_retry_on_startup = True
    CELERY_BEAT_SCHEDULE = {
        'fetch_data': {
            'task': 'tasks.fetch_data',
            'schedule': crontab(minute=0, hour='*/1'),  # Run every hour
        },
    }
