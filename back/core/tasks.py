# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from celery.task import periodic_task
from celery.schedules import crontab
from datetime import timedelta


@shared_task
def add(x, y):
    return x + y


@periodic_task(run_every=timedelta(seconds=20), name="Check all ")
def check_all_file_repos():
    """ Get all files that have repo, and check them for update """
    print("Test task OK")


@periodic_task(run_every=crontab(minute=1), name="test_task2")
def test_task2():
    print("Test task2 OK")
