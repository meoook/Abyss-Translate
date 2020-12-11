import logging

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, MaxRetriesExceededError

from core.models import Folder, Translated
from core.services.file_interface.file_interface import FileInterface

from core.services.folder_interface import LocalizeGitFolderInterface

logger = logging.getLogger('django')


@shared_task(
    name="T1: Update file from repo then parse it",
    max_retries=2,
    # soft_time_limit=5,
    # time_limit=20,
    # rate_limit='2/h',
    ignore_result=True
)
def file_uploaded_new(file_id, original_lang_id, file_path):
    """ After file uploaded -> If possible update it from repo then get info and build new translates """
    file_manager = FileInterface(file_id)
    logger.info(f'File id:{file_id} try update from repo and parse')
    file_manager.file_new(file_path, original_lang_id)


@shared_task(
    name="T2: Update translates from uploaded file",
    max_retries=2,
    # soft_time_limit=5,
    # time_limit=20,
    # rate_limit='2/h',
    ignore_result=True
)
def file_uploaded_refresh(file_id, lang_id, tmp_path, is_original):
    """ After copy or new original uploaded -> Get info and rebuild translates for language """
    file_manager = FileInterface(file_id)
    _settings_to_msg = f'language:{lang_id} as {"original" if is_original else "translates"}'
    logger.info(f'File id:{file_id} loaded new data for {_settings_to_msg}')
    file_manager.file_refresh(tmp_path, lang_id, is_original)


@shared_task(
    name="T3: Git repository url changed",
    max_retries=0,
    soft_time_limit=5,
    time_limit=15,
    # rate_limit='12/h',
    ignore_result=True
)
def folder_update_repo_after_url_change(folder_id):
    """ After changing git url -> Update folder files from git repository folder """
    try:
        folder_manager = LocalizeGitFolderInterface(folder_id)
        folder_manager.repo_url_changed()
        folder_manager.update_files()
    except SoftTimeLimitExceeded:
        logger.warning(f'Checking folder id:{folder_id} too slow')


@shared_task(
    name="T4: Git repository access changed",
    max_retries=0,
    soft_time_limit=5,
    time_limit=15,
    # rate_limit='12/h',
    ignore_result=True
)
def folder_repo_change_access_and_update(folder_id, access_type, access_value):
    """ After changing git access -> Update folder files from git repository folder """
    try:
        folder_manager = LocalizeGitFolderInterface(folder_id)
        folder_manager.change_repo_access(access_type, access_value)
        folder_manager.update_files()
    except SoftTimeLimitExceeded:
        logger.warning(f'Checking folder id:{folder_id} too slow')


@shared_task(
    name="T5: Delete project or folder",
    max_retries=0,
    soft_time_limit=2,
    time_limit=5,
    ignore_result=True
)
def delete_folder_object(obj_id, obj_type='folder'):
    """ After delete project or folder -> Delete in database and in file system """
    try:
        pass
    except SoftTimeLimitExceeded:
        logger.warning(f'Checking {"folder" if obj_type == "folder" else "project"} id:{obj_id} too slow')


@shared_task(
    # name="P1: (2h) Update users files from git repositories",
    name="check_all_file_repos",
    # run_every=crontab(minute=0, hour='*/2'),
    max_retries=0,
    soft_time_limit=110,
    time_limit=120,
    # rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def check_all_file_repos():
    """ It's a global app task -> Get all users files check git status and update if needed """
    # GET ALL FOLDERS
    logger.info('Update all files in folders where repo status is ok')
    try:
        folders_with_repo = Folder.objects.filter(repo_status=True)
        for folder in folders_with_repo:
            folder_manager = LocalizeGitFolderInterface(folder.id)
            folder_manager.update_files()
    except SoftTimeLimitExceeded:
        logger.warning('Checking files too slow')


@shared_task(
    # name="P2: (2h) Update users copy files in git repositories",
    name="refresh_copies",
    # run_every=crontab(minute=0, hour='*/2'),
    max_retries=0,
    soft_time_limit=110,
    time_limit=120,
    # rate_limit='1/h',
    ignore_result=True,
    store_errors_even_if_ignored=True
)
def refresh_copies():
    """ It's a global app task -> Get all users files check git status and update if needed """
    # GET ALL FOLDERS
    logger.info('Refresh all copies witch translates updated')
    try:
        for copy_info in Translated.objects.filter(need_refresh=True).values('file__id', 'language__id'):
            file_manager = FileInterface(copy_info['file__id'])
            file_manager.translated_copy_refresh(copy_info['language__id'])
    except SoftTimeLimitExceeded:
        logger.warning('Creating copies too slow')
