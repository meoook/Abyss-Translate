# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации, оставляя для переводчика только
**_полезный текст_**, отсекая _технические данные_.

    site: (localize.ru)[localize.eee.ru]
    version: 0.2.2
    author: meok
    build: react, django, postgres, celery, redis, (nginx)

## Функции приложения:

- [x] управление проектами
- [x] загрузка файла (API)
- [x] автоматический парсинг файла (**html**, **csv**, **po**)
- [ ] создание переведенных копий и их выгрузка через API
- [x] роли пользователей и проверки
- [ ] авторизация с сервера abyss
- [x] работа с гит репозиториями (API)
- [x] расписание задач
- [x] логирование
- [ ] ручная обработка файла
- [ ] тестирование функций
- [ ] тестирование нагрузки

## Поддержка гит провайдеров:

- [x] **github**
- [x] **bitbucket**
- [ ] **gitlab**

## Заданя Celery

- [x] Парсинг файла (удалить)
- [ ] Обновление файла в гит репозитории (если возможно) и последующий парсинг
- [ ] Создание переведенной копии и размещении ее в гит репозитории (если возможно)
- [ ] Удаление файлов и папок
- [x] Проверка файла в гите для обновления (удалить)
- [ ] Изменение URL репозитория гита для папки
- [ ] Проверка файлов в гите на обновление **by hash**
- [ ] Загрузка переведенных копий в гит если **hash updated** или новая (удалить)

## Зависимости

Для работы приложения необходим **Docker 19.03.12**

```sh
$ apt-get install -y docker
$ docker --version
Docker version 19.03.8, build afacb8b7f0
```

и **Docker-Compose 1.26.2**

```sh
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
docker-compose version 1.26.2, build 1110ad01
```

> For alpine, the following dependency packages are needed:
> `py-pip`, `python-dev`, `libffi-dev`, `openssl-dev`, `gcc`, `libc-dev`, and `make`.

## Запуск приложения

из папки приложения выполняем

```sh
$ docker-compose up -d --build
```

или

```sh
$ sh ./runner.sh 5
```

## Release notes

| version | changes                                                          |
| ------- | ---------------------------------------------------------------- |
| 0.04.0  | Система прав пользователей, роль - creator                       |
| 0.03.8  | Тесты для API авторизации и проектов                             |
| 0.03.7  | Управляющий модуль runner.sh для управления docker и приложением |
| 0.03.6  | Celery: Задача по загрузке файла                                 |
| 0.03.5  | Управляющий класс для файлов, доработка services                 |
| 0.03.4  | Служебные функции в классы services                              |
| 0.03.3  | Сервера: redis, celery - настройка                               |
| 0.03.2  | Docker - окружение dev и немного prod                            |
| 0.03.1  | Система логирования                                              |
| 0.03.0  | Перевод сервера в Docker                                         |
| 0.02.11 | Гит: обновление ссылки для папки - проверка всех файлов          |
| 0.02.10 | Гит: проверка файла, скачивание - github, bitbucket              |
| 0.02.9  | Модуль для работы с гит репозиториями                            |
| 0.02.8  | Создание переведенной копии + скачивание                         |
| 0.02.7  | Прогресс перевода файла                                          |
| 0.02.6  | Фильтрация на странице для перевода текстов                      |
| 0.02.5  | Страница для перевода текстов                                    |
| 0.02.4  | Переработка модели: метки - переводы (оригиналов нет)            |
| 0.02.3  | Парсинг файла: метод csv (доработка модели)                      |
| 0.02.2  | Парсинг файла: метод ue, html                                    |
| 0.02.1  | Модель для хранения оригиналов и переводов текста                |
| 0.02.0  | Парсинг файла: получение информации о файле                      |
| 0.01.8  | Отображение файлов (mock data)                                   |
| 0.01.8  | Менюшки для управления проектами и папками                       |
| 0.01.6  | Загрузка файлов через браузер (DropZone)                         |
| 0.01.6  | Управление файлами и папками (API)                               |
| 0.01.5  | Загрузка файлов (API)                                            |
| 0.01.4  | knox авторизация (по токену)                                     |
| 0.01.3  | Базовый интерфейс для управления проектами и папками             |
| 0.01.2  | API на текущую модель                                            |
| 0.01.1  | Модель приложения: языки, проекты, папки                         |

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
        else:
            language_to_add.save()
```

...

```py
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
