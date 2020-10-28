import os
import uuid

from django.contrib.postgres.indexes import GinIndex, BTreeIndex
from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save

import django.contrib.postgres.search as pg_search

# class Profiles(models.Model):
#     USER_ROLE_CHOICES = [
#         (0, 'admin'),
#         (3, 'moderator'),
#         (5, 'game creator'),
#         (8, 'translator'),
#         (10, 'no role user'),
#     ]
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
#     role = models.SmallIntegerField(default=10, choices=USER_ROLE_CHOICES)
#
#
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         profile, created = Profiles.objects.get_or_create(user=instance)
#
#
# post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)


class Language(models.Model):
    """ Language loaded on start. Need to set active -> True to display it on API """
    name = models.CharField(max_length=50, null=False)
    short_name = models.CharField(max_length=10, null=False)
    active = models.BooleanField(default=False)
    regular = models.CharField(max_length=50, blank=True)   # MB shorter or JSON

    def __str__(self):
        return self.name


class Project(models.Model):
    """ Set up default languages and namespace. Folder created by ID. """
    save_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon_chars = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)
    lang_orig = models.ForeignKey(Language, on_delete=models.DO_NOTHING, related_name='projects')
    translate_to = models.ManyToManyField(Language, related_name='projects_m')

    class Meta:
        unique_together = ['owner', 'name']
        permissions = [
            ("creator", "Can create projects and invite"),
            ("admin", "Can manage projects where invited"),
            ("translator", "Can translate files from projects where invited"),
        ]


class ProjectPermission(models.Model):
    """ Permissions for project """
    PROJECT_PERMISSION_CHOICES = [
        (0, 'tranlate'),            # Can translate files in project
        (5, 'invite translator'),   # Default admin role (can change permission 0 to other users)
        (8, 'manage'),              # Can create\delete\update - folders\files
        (9, 'admin'),               # Can change permissions to other admins (change permission 5, 8)
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    permission = models.SmallIntegerField(choices=PROJECT_PERMISSION_CHOICES)

    class Meta:
        unique_together = ['user', 'project', 'permission']


class Folder(models.Model):
    """" Folder model with auto delete. Folder created by ID. """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    repo_url = models.URLField(blank=True)
    repo_status = models.BooleanField(null=True)    # Null when connecting\checking

    class Meta:
        unique_together = [('position', 'project'), ('name', 'project')]


class FolderRepo(models.Model):
    """ Version control repository manager details """
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, primary_key=True)
    provider = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    sha = models.CharField(max_length=40, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    access = models.JSONField(null=True)
    error = models.CharField(max_length=255, blank=True)    # Access, exist or other errors


def user_directory_path(instance, filename):
    """ File will be uploaded to users/<username>/<prj_id>/<folder_id>/<filename> """
    folder = instance.folder
    return '{}/{}/{}/{}'.format(folder.project.owner, folder.project.id, folder.id, filename)


class File(models.Model):
    """" File model with auto delete. File is unique for folder. """

    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    codec = models.CharField(max_length=20, blank=True)
    method = models.CharField(max_length=10, blank=True)    # csv, ue, html
    options = models.JSONField(null=True)           # csv delimiter and fields, quotes. Mb some info about PO files.
    data = models.FileField(upload_to=user_directory_path, max_length=255, storage=settings.STORAGE_ROOT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)           # File updated
    items = models.PositiveIntegerField(null=True)          # FileMark count
    words = models.PositiveIntegerField(null=True)          # Total words count
    repo_sha = models.CharField(max_length=40, blank=True)  # Repository hash for this version of file
    repo_status = models.BooleanField(null=True)            # Null - no repo for related Folder
    lang_orig = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    warning = models.CharField(max_length=255, blank=True)  # To handle warnings (language or other checks errors)
    error = models.CharField(max_length=255, blank=True)    # Parsing or save on disk problems

    class Meta:
        unique_together = ['folder', 'name']


class Translated(models.Model):
    """ File translate progress and language copy """
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    items = models.PositiveIntegerField(default=0)  # To count total progress
    finished = models.BooleanField(default=False)   # All items have translations
    checked = models.BooleanField(default=False)    # Translations checked by admin?
    translate_copy = models.FileField(max_length=255, blank=True, storage=settings.STORAGE_ROOT)
    repo_sha = models.CharField(max_length=40, blank=True)  # Not always hash - can be information about update status

    class Meta:
        unique_together = ['file', 'language']


class ErrorFiles(models.Model):
    """ Put files here to analyze to upgrade check system """
    data = models.FileField(upload_to='%Y/%m/%d/', max_length=255, storage=settings.STORAGE_ERRORS)
    error = models.CharField(max_length=255)


class FileMark(models.Model):
    """ Mark targets where translate must be placed in file (based on method). """
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    fid = models.CharField(max_length=100, db_index=True)    # fid for UE and CSV method, position:tag for html
    words = models.PositiveIntegerField()                    # Words amount in all items for mark
    search_words = models.TextField()                        # Words to find mark
    context = models.TextField()                             # File context for translator help
    deleted = models.BooleanField(default=False)             # If this mark not found in new version of file

    class Meta:
        unique_together = ['file', 'fid']


class MarkItem(models.Model):
    """ Each mark can have several items inside (like cols:csv or variants:ue) """
    mark = models.ForeignKey(FileMark, on_delete=models.CASCADE)
    item_number = models.PositiveIntegerField()          # Col for CSV
    md5sum = models.CharField(max_length=32)             # Check same values
    md5sum_clear = models.CharField(max_length=32)       # Help translate - MD5 without special chars or digits
    words = models.PositiveIntegerField()                # Words amount in item (less then 2 letters - no count)

    class Meta:
        unique_together = ['mark', 'item_number']


class Translate(models.Model):
    """ Translate to language for mark item """
    translator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    mark = models.ForeignKey(FileMark, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    text = models.TextField()  # db_index=True
    # words = pg_search.SearchVectorField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    checked = models.BooleanField(default=False)
    checker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='checker')
    warning = models.CharField(max_length=255, blank=True)  # No errors means - text translated

    class Meta:
        unique_together = ['mark', 'language']
        indexes = [GinIndex(fields=['text'], name='core_transl_text_gin')]
        # indexes = [BTreeIndex(fields=['text'], opclasses=("text_ops", ), name='core_transl_text_gintrgm')]


class TranslateChangeLog(models.Model):
    """ Translate log """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    translate = models.ForeignKey(Translate, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)


def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes file from filesystem when corresponding `File` or `Translated` object is deleted. """
    if sender._meta.model_name == 'files':
        inst_obj = instance.data
    elif sender._meta.model_name == 'translated':
        if instance.finished and instance.translate_copy:
            inst_obj = instance.translate_copy
        else:
            return
    else:
        print("Error: trigger auto_delete_file_on_delete - input wrong instance")
        return
    if os.path.isfile(inst_obj.path):
        print('Delete file -> onDelete File object', inst_obj.path)
        # os.remove(instance.file.path)
        inst_obj.delete(save=False)


# TODO: for prj and folder -> one function
def auto_delete_folder_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Folder` object is deleted. """
    path_to_delete = '{}/{}/{}/'.format(instance.project.owner.username, instance.project.id, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete folder -> onDelete Folder object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)


def auto_delete_project_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Project` object is deleted. """
    path_to_delete = '{}/{}/'.format(instance.owner.username, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete project folder -> onDelete Project object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)


post_delete.connect(auto_delete_file_on_delete, sender=File)
post_delete.connect(auto_delete_file_on_delete, sender=Translated)
post_delete.connect(auto_delete_folder_on_delete, sender=Folder)
post_delete.connect(auto_delete_project_on_delete, sender=Project)
