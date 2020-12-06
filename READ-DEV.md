# Help for development

Всякая всячина для разработки приложения - (что бы не забыть лист)

## Функция для автомиграции языков 💎 5%

```py
from django.conf.global_settings import LANGUAGES
from django.contrib.postgres.operations import BtreeGinExtension


def get_languages(apps, schema_editor):
    languages = apps.get_model('core', 'Language')
    for language in LANGUAGES:
        language_to_add = languages(name=language[1], short_name=language[0])
        if language[0] in ('en', 'ru', 'de', 'es'):
            language_to_add.active = True
        language_to_add.save()
    ...
        migrations.RunPython(get_languages),
    ...
        BtreeGinExtension(),
```


# FIX IT

```shell script
redis_1 | WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
redis_1 | WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
```

### Bitbucket URL to add app
https://bitbucket.org/meokok/workspace/settings/oauth-consumers/new

### OAuth simple APP
https://bitbucket.org/atlassian/bb-cloud-auth-code-grant-sample-app/src/master/

### Send mail

```python
from django.core import mail

with mail.get_connection() as connection:
    mail.EmailMessage(
        subject1, body1, from1, [to1],
        connection=connection,
    ).send()
    mail.EmailMessage(
        subject2, body2, from2, [to2],
        connection=connection,
    ).send()
```
###
```shell script
command: sh -c "python manage.py migrate --no-input && gunicorn localize.wsgi --workers 3 -b 0.0.0.0:8000"
```

### Покрытие тестами

```shell script
coverage run --source='.' ./manaage.py test .
coverage report
coverage html
```

### Добавить PATH 🏆 12%

end :+1:

```shell script
export PATH="/usr/xaxa/bin:$PATH"
```

### class ModelViewSet

```
mixins.CreateModelMixin,
mixins.RetrieveModelMixin,
mixins.UpdateModelMixin,
mixins.DestroyModelMixin,
mixins.ListModelMixin,
GenericViewSet
```

```
from django.contrib.postgres.indexes import GinIndex


class GinSpaceConcatIndex(GinIndex):

    def get_sql_create_template_values(self, model, schema_editor, using):

        fields = [model._meta.get_field(field_name) for field_name, order in self.fields_orders]
        tablespace_sql = schema_editor._get_index_tablespace_sql(model, fields)
        quote_name = schema_editor.quote_name
        columns = [
            ('%s %s' % (quote_name(field.column), order)).strip()
            for field, (field_name, order) in zip(fields, self.fields_orders)
        ]
        return {
            'table': quote_name(model._meta.db_table),
            'name': quote_name(self.name),
            'columns': "({}) gin_trgm_ops".format(" || ' ' || ".join(columns)),
            'using': using,
            'extra': tablespace_sql,
        }
```
