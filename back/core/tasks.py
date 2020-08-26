from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from celery.exceptions import SoftTimeLimitExceeded, MaxRetriesExceededError

from core.services.file_manager import LocalizeFileManager

from datetime import timedelta

logger = logging.getLogger('logfile')


# retries=3, default_retry_delay=1
@shared_task(
    name="T1: Update file from repo then parse it",
    max_retries=2,
    # soft_time_limit=5,
    # time_limit=20,
    # rate_limit='2/h',
    ignore_result=True
)
def file_parse_uploaded(file_id, new=True):
    """ After file uploaded -> If possible update it from repo then get info and parse data into text to translate """
    file_manager = LocalizeFileManager(file_id)
    try:
        if file_manager.error or not file_manager.parse():
            logger.warning(f'File parse error id:{file_id} err: {file_manager.error}')
            file_parse_uploaded.retry()
    except MaxRetriesExceededError:
        err_file_id, err_msg = file_manager.save_error()
        logger.error(f'File id:{file_id} parse retries limit. Created error file (id:{err_file_id}) saved: {err_msg}')
    if new:
        file_manager.create_progress()


@shared_task(
    name="T2: Create translated copy of file then upload to repo",
    max_retries=2,
    # soft_time_limit=5,
    # time_limit=20,
    # rate_limit='2/h',
    ignore_result=True
)
def file_create_translated(file_id, lang_id):
    """ After file translated to language -> Create translated copy of this file then create or update in repo """
    file_manager = LocalizeFileManager(file_id)
    try:
        if file_manager.error or not file_manager.create_translated_copy():
            file_create_translated.retry()
    except MaxRetriesExceededError:
        logger.critical(f'File create translated copy retries limit')


@shared_task(
    name="T3: Update folder files from git repository folder",
    max_retries=1,
    soft_time_limit=1,
    time_limit=5,
    rate_limit='12/h',
    ignore_result=True
)
def folder_update_repo_url(filo):
    """ After changing git url -> Update folder files from git repository folder """
    return True


@periodic_task(
    name="P1: (3h) Update users files from git repositories",
    run_every=crontab(minute=0, hour='*/3'),
    max_retries=0,
    soft_time_limit=30,
    time_limit=60,
    # rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def check_all_file_repos():
    """ It's a global app task -> Get all users files check git status and update if needed """
    try:
        logger.info('Checking files too slow')
    except SoftTimeLimitExceeded:
        logger.warning('Checking files too slow')
    return True


# @periodic_task(
#     name="P1: (4m) Upload translated files into git repositories",
#     run_every=crontab(minute='*/4'),
#     max_retries=2,
#     soft_time_limit=30,
#     time_limit=59,
#     # rate_limit='1/h',
#     ignore_result=True,
#     store_errors_even_if_ignored=True
# )
# def upload_all_translated():
#     """ It's a global app task -> Get all users translated files and upload them in git repos """
#     # TODO: Do we need this task ?
#     try:
#         logger.info('Checking files too slow')
#     except SoftTimeLimitExceeded:
#         logger.warning('Checking files too slow')
#     return True


@periodic_task(run_every=crontab(minute=0, hour='*/1'), name="P0: (1h) Check celery. Run each hour.")
def test_task():
    logger.error('TEST CELERY ERROR')
    return True
