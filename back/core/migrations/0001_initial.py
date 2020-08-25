# Generated by Django 3.1 on 2020-08-22 15:31

import core.models
from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf.global_settings import LANGUAGES


def get_languages(apps, schema_editor):
    languages = apps.get_model('core', 'Languages')
    for language in LANGUAGES:
        language_to_add = languages(name=language[1], short_name=language[0])
        if language[0] in ('en', 'ru', 'de', 'es'):
            language_to_add.active = True
            language_to_add.save()
        else:
            language_to_add.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.FileField(max_length=255, storage=django.core.files.storage.FileSystemStorage(base_url='/errors/', location='/usr/src/back/users/errors'), upload_to='%Y/%m/%d/')),
                ('error', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='FileMarks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark_number', models.PositiveIntegerField()),
                ('col_number', models.PositiveIntegerField(null=True)),
                ('options', models.JSONField(null=True)),
                ('md5sum', models.CharField(max_length=32)),
                ('md5sum_clear', models.CharField(max_length=32)),
                ('words', models.PositiveIntegerField()),
                ('text_binary', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='Folders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=50)),
                ('repo_url', models.URLField(blank=True)),
                ('repo_status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Languages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=10)),
                ('active', models.BooleanField(default=False)),
                ('regular', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Translates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('checked', models.BooleanField(default=False)),
                ('checker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checker', to=settings.AUTH_USER_MODEL)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.languages')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.filemarks')),
                ('translator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('mark', 'language')},
            },
        ),
        migrations.CreateModel(
            name='FolderRepo',
            fields=[
                ('folder', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.folders')),
                ('provider', models.CharField(max_length=100)),
                ('owner', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('path', models.CharField(blank=True, max_length=100)),
                ('branch', models.CharField(blank=True, max_length=100)),
                ('hash', models.CharField(blank=True, max_length=40, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('access', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TranslatesChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('translate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.translates')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('save_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('icon_chars', models.CharField(max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lang_orig', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='core.languages')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('translate_to', models.ManyToManyField(related_name='projects_m', to='core.Languages')),
            ],
            options={
                'permissions': [('creator', 'Can create projects and invite'), ('admin', 'Can manage projects where invited'), ('translator', 'Can translate files from projects where invited')],
                'unique_together': {('owner', 'name')},
            },
        ),
        migrations.AddField(
            model_name='folders',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.projects'),
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('state', models.SmallIntegerField(choices=[(0, 'error'), (1, 'uploaded'), (2, 'parsed')], default=1)),
                ('codec', models.CharField(blank=True, max_length=20)),
                ('method', models.CharField(blank=True, max_length=10)),
                ('options', models.JSONField(null=True)),
                ('data', models.FileField(max_length=255, storage=django.core.files.storage.FileSystemStorage(base_url='/users/', location='/usr/src/back/users'), upload_to=core.models.user_directory_path)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('items', models.PositiveIntegerField(null=True)),
                ('words', models.PositiveIntegerField(null=True)),
                ('repo_hash', models.CharField(blank=True, max_length=40)),
                ('repo_status', models.BooleanField(null=True)),
                ('error', models.CharField(blank=True, max_length=255)),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.folders')),
                ('lang_orig', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.languages')),
            ],
            options={
                'unique_together': {('folder', 'name')},
            },
        ),
        migrations.AddField(
            model_name='filemarks',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.files'),
        ),
        migrations.CreateModel(
            name='Translated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.PositiveIntegerField(default=0)),
                ('finished', models.BooleanField(default=False)),
                ('checked', models.BooleanField(default=False)),
                ('translate_copy', models.FileField(blank=True, max_length=255, storage=django.core.files.storage.FileSystemStorage(base_url='/users/', location='/usr/src/back/users'), upload_to='')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.files')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.languages')),
            ],
            options={
                'unique_together': {('file', 'language')},
            },
        ),
        migrations.CreateModel(
            name='ProjectPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.SmallIntegerField(choices=[(0, 'tranlate'), (5, 'invite translator'), (8, 'manage'), (9, 'admin')])),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.projects')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'project', 'permission')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='folders',
            unique_together={('position', 'project'), ('name', 'project')},
        ),
        migrations.AlterUniqueTogether(
            name='filemarks',
            unique_together={('file', 'mark_number', 'col_number')},
        ),
        migrations.RunPython(get_languages),
    ]
