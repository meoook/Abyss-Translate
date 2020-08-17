from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from celery.exceptions import SoftTimeLimitExceeded

from services.file_manager import LocalizeFileManager

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
def file_parse(file_id):
    """ Get file info and parse file data into text to translate """
    file_manager = LocalizeFileManager(file_id)
    if not file_manager.success or not file_manager.parse():
        if file_parse.request.retries < 3:
            file_parse.retry()


@shared_task(
    name="Update file from git repository",
    max_retries=2,
    soft_time_limit=1,
    time_limit=5,
    rate_limit='1/h',
    ignore_result=True
)
def file_update_from_repo(filo):
    """ After adding new file by user -> Check (exist & access) and update file in repository folder files """
    return True


@shared_task(
    name="Update files in git repository folder",
    max_retries=1,
    soft_time_limit=1,
    time_limit=5,
    rate_limit='4950/h',
    ignore_result=True
)
def folder_update_by_repo(filo):
    """ After changing git url -> Update folder files in git repository folder """
    return True

@periodic_task(
    name="Update users files from git repositories",
    run_every=crontab(hour='*/1'),
    max_retries=0,
    soft_time_limit=30,
    time_limit=59,
    rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def check_all_file_repos():
    """ It's a global app task -> Get all users files check git status and update if needed """
    try:
        pass
    except SoftTimeLimitExceeded:
        logger.warning('Checking files too slow')
        pass

@periodic_task(
    name="Upload translated files into git repositories",
    run_every=crontab(hour='*/1'),
    max_retries=0,
    soft_time_limit=30,
    time_limit=59,
    rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def check_all_file_repos():
    """ It's a global app task -> Get all users translated files and upload them in git repos """
    try:
        pass
    except SoftTimeLimitExceeded:
        logger.warning('Checking files too slow')
        pass


@periodic_task(run_every=timedelta(seconds=10), name="Task to check celery. Run each 10 seconds.")
def test_task():
    logger.error('TEST ERROR')
