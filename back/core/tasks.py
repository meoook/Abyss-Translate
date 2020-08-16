from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from celery.exceptions import SoftTimeLimitExceeded

from datetime import timedelta

logger = logging.getLogger('logfile')


@shared_task(
    name="Parse file",
    max_retries=2,
    soft_time_limit=5,
    time_limit=20,
    rate_limit='1/h',
    ignore_result=True
)
def file_parse(filo):
    """ Get file info and parse file data into text to translate """
    return True


@periodic_task(
    name="Check users files",
    run_every=crontab(hour='*/1'),
    max_retries=0,
    soft_time_limit=30,
    time_limit=59,
    rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def check_all_file_repos():
    """ It's a global app task. Get all users files that have repository, and check them for update. """
    try:
        pass
    except SoftTimeLimitExceeded:
        logger.warning('Checking files too slow')
        pass


@periodic_task(run_every=timedelta(seconds=10), name="Task to check celery. Run each 10 seconds.")
def test_task():
    logger.error('TEST ERROR')
