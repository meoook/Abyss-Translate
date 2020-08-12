import os
import uuid

from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save


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


class Languages(models.Model):
    """ Languages loaded on start. Need to set active -> True to display it on API """
    name = models.CharField(max_length=50, null=False)
    short_name = models.CharField(max_length=10, null=False)
    active = models.BooleanField(default=False)
    regular = models.CharField(max_length=50, blank=True)   # MB shorter or JSON

    def __str__(self):
        return self.name

    # class Meta:
    #     db_table = 'app_languages'
    #     verbose_name_plural = 'App Languages'


class Projects(models.Model):
    """ Set up default languages and namespace. Folder created by ID. """
    save_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon_chars = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    lang_orig = models.ForeignKey(Languages, null=True, on_delete=models.DO_NOTHING, related_name='projects')
    translate_to = models.ManyToManyField(Languages, related_name='projects_m')

    class Meta:
        unique_together = ['owner', 'name']


class Folders(models.Model):
    """" Folder model with auto delete. Folder created by ID. """
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    repository = models.URLField(null=True, blank=True)

    class Meta:
        # db_table = 'folders'
        # verbose_name_plural = 'Users Folders'
        unique_together = [('position', 'project'), ('name', 'project')]


class ProjectPermissions(models.Model):
    """ Admin permissions for project """
    PROJECT_PERMISSION_CHOICES = [
        (0, 'invite translator'),   # Default admin role
        (1, 'manage'),              # Can create\delete\update - folders\files
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    permission = models.SmallIntegerField(choices=PROJECT_PERMISSION_CHOICES)


class FolderRepo(models.Model):
    """ Version control repository manager details """
    folder = models.OneToOneField(Folders, on_delete=models.CASCADE, primary_key=True)
    provider = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    hash = models.CharField(max_length=40, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    access = models.JSONField(null=True)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    project = Folders.objects.get(id=instance.folder.id).project
    new_path = '{}/{}/{}/{}'.format(instance.owner, project.id, instance.folder.id, filename)
    return new_path


class Files(models.Model):
    """" File model with auto delete. File is unique for folder. """
    # TODO: FileStats - @property
    FILE_STATE_CHOICES = [
        (0, 'deleted'),
        (1, 'uploaded'),     # Is parsing
        (2, 'parsed'),       # Ready to translate
        (3, 'parse error'),  # Error while parsing
        (4, 'started'),      # Order created
        (5, 'translated'),   # Have all translations\ Order finish
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folders, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    state = models.SmallIntegerField(choices=FILE_STATE_CHOICES, default=1)
    method = models.CharField(max_length=10)
    options = models.JSONField(null=True)      # csv delimiter and fields, quotes,
    data = models.FileField(upload_to=user_directory_path, max_length=255, storage=settings.STORAGE_ROOT)
    md5sum = models.CharField(max_length=32)    # TODO: Do we need it ?
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)   # File updated
    new_translate_time = models.DateTimeField(null=True)
    items_count = models.PositiveIntegerField(null=True)
    words = models.PositiveIntegerField(null=True)
    repo_hash = models.CharField(max_length=40, blank=True)     # TODO: Check max length
    repo_founded = models.BooleanField(null=True)   # Null - no repo for related Folder
    codec = models.CharField(max_length=20)
    lang_orig = models.ForeignKey(Languages, on_delete=models.DO_NOTHING, related_name='files')
    translate_to = models.ManyToManyField(Languages, related_name='files_m')
    number_top_rows = models.PositiveSmallIntegerField(null=True)   # Header
    number_bot_rows = models.PositiveSmallIntegerField(null=True)   # Footer

    class Meta:
        # db_table = 'folders'
        # verbose_name_plural = 'Users Folders'
        unique_together = [('owner', 'folder', 'name')]


class Translated(models.Model):
    """ File translate progress and language copy """
    file = models.ForeignKey(Files, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.DO_NOTHING)
    items_count = models.PositiveIntegerField(default=0)
    # words = models.PositiveIntegerField(default=0)
    finished = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    translate_copy = models.FileField(max_length=255, blank=True)   # storage=settings.STORAGE_ROOT,

    class Meta:
        unique_together = [('file', 'language')]


class ErrorFiles(models.Model):
    """ If file codec or language not detected - file put here to upgrade check system """
    data = models.FileField(upload_to='%Y/%m/%d/', max_length=255, storage=settings.STORAGE_ERRORS)
    error = models.CharField(max_length=255)


class FileMarks(models.Model):
    """ Mark targets where translate must be placed in file (based on method). """
    file = models.ForeignKey(Files, on_delete=models.CASCADE)
    mark_number = models.PositiveIntegerField()
    col_number = models.PositiveIntegerField(null=True)  # For CSV method
    options = models.JSONField(null=True)                       # key for UE method, tag for html,
    md5sum = models.CharField(max_length=32)             # Check same values
    md5sum_clear = models.CharField(max_length=32)       # Help translate - MD5 without special chars or digits
    words = models.PositiveIntegerField()                # The words more then 2 letter count
    text_binary = models.BinaryField()                   # To replace when creating file
    # deleted = models.BooleanField(default=False)       # If this mark not found in new version of file

    class Meta:
        unique_together = [('file', 'mark_number', 'col_number')]


class Translates(models.Model):
    """ Translates """
    translator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    mark = models.ForeignKey(FileMarks, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.DO_NOTHING)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    checked = models.BooleanField(default=False)
    checker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='checker')

    class Meta:
        unique_together = [('mark', 'language')]


class TranslatesChangeLog(models.Model):
    """ Translates log """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    translate = models.ForeignKey(Translates, on_delete=models.CASCADE)
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
        print('Delete file -> onDelete Files object', inst_obj.path)
        # os.remove(instance.file.path)
        inst_obj.delete(save=False)


def auto_delete_folder_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Folder` object is deleted. """
    path_to_delete = '{}/{}/{}/'.format(instance.project.owner.username, instance.project.id, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete folder -> onDelete Folders object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)


def auto_delete_project_on_delete(sender, instance, **kwargs):
    """ TRIGGER: Deletes folder from filesystem when corresponding `Folder` object is deleted. """
    path_to_delete = '{}/{}/'.format(instance.owner.username, instance.id)
    folder = os.path.join(settings.MEDIA_ROOT, path_to_delete)
    if os.path.isdir(folder):
        print('Delete project folder -> onDelete Projects object', folder)
        settings.STORAGE_ROOT.delete(path_to_delete)


post_delete.connect(auto_delete_file_on_delete, sender=Files)
post_delete.connect(auto_delete_file_on_delete, sender=Translated)
post_delete.connect(auto_delete_folder_on_delete, sender=Folders)
post_delete.connect(auto_delete_project_on_delete, sender=Projects)
