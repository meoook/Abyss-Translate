from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from celery.task import periodic_task

from celery.schedules import crontab
from datetime import timedelta

logger = logging.getLogger('logfile')

@shared_task(name="Get file info then parse")
def file_parse(filo):
    """ Get file info and parse file data into text to translate """
    return filo


@periodic_task(run_every=crontab(minute='*/1'), name="Check all files connected to repository folder")
def check_all_file_repos():
    """ Get all files that have repository, and check them for update """
    logger.warning('TEST WARNING')


@periodic_task(run_every=timedelta(seconds=10), name="Task to check celery. Run each 10 seconds.")
def test_task():
    logger.error('TEST ERROR')
