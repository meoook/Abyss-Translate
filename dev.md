# Help for development

Всякая всячина для разработки приложения - (что бы не забыть лист)

## Функция для автомиграции языков 💎 5%

```py
from django.conf.global_settings import LANGUAGES

def get_languages(apps, schema_editor):
    languages = apps.get_model('core', 'Languages')
    for language in LANGUAGES:
        language_to_add = languages(name=language[1], short_name=language[0])
        if language[0] in ('en', 'ru', 'de', 'es'):
            language_to_add.active = True
        language_to_add.save()
    ...
        migrations.RunPython(get_languages),
```

## Добавить PATH 🏆 12%

end :+1:

```
export PATH="/usr/xaxa/bin:$PATH"
```

## class ModelViewSet

```
mixins.CreateModelMixin,
mixins.RetrieveModelMixin,
mixins.UpdateModelMixin,
mixins.DestroyModelMixin,
mixins.ListModelMixin,
GenericViewSet
```
