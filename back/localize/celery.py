import os
from celery import Celery
from celery.schedules import crontab
# from core.tasks import check_all_file_repos

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localize.settings')
app = Celery('localize')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'files-update-from-repo': {
        'task': 'check_all_file_repos',
        'schedule': crontab(minute=0, hour='*/2'),
        # 'args': (16, 16)
    },
    'copy-refresh-then-to-repo': {
        'task': 'refresh_copies',
        'schedule': crontab(minute=0, hour='1/2'),
        # 'args': (16, 16)
    },
}

# @app.on_after_configure.connect
# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(crontab(minute=0, hour='*/3'), check_all_file_repos, name='add every 10')
