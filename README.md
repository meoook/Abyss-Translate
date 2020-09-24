# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации, оставляя для переводчика только
**_полезный текст_**, отсекая _технические данные_.

    site: (localize.ru)[localize.eee.ru]
    version: 0.4.2
    author: meok
    build: react, django, postgres, celery, redis, nginx

## Функции приложения:

- [x] управление проектами
- [x] загрузка файла (API)
- [x] автоматический парсинг файла (**html**, **csv**, **po**)
- [x] создание переведенных копий и их выгрузка через API
- [x] роли пользователей и проверки
- [ ] авторизация с сервера abyss
- [x] работа с гит репозиториями (API)
- [x] расписание задач
- [x] логирование
- [ ] ручная обработка файла

## Поддержка гит провайдеров:

- [x] **github**
- [x] **bitbucket** (только на чтение открытых репозиториев)
- [x] **gitlab**

## Заданя Celery

- [x] T1: Обновление файла в гит репозитории (если возможно) и последующий парсинг
- [x] T2: Создание переведенной копии и размещении ее в гит репозитории (если возможно)
- [x] T3: Изменение URL репозитория для папки
- [ ] T4: Удаление файлов и папок
- [x] P1: Проверка файлов в репозиториях на обновление **by hash**

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

| version | date     | changes                                                            |
| ------- | -------- | ------------------------------------------------------------------ |
|         |          | Merge check - отображение изменений                                |
|         |          | Переработка способов парсинга файлов                               |
|         |          | Save all "good" translates for search database                     |
|         |          | Docker: pg_bouncer                                                 |
|         |          | Что делать после ввода перевода для текста (проверки языка и т.п.) |
|         |          | More translate filters or sorters (by like 70%)                    |
|         |          | Переработка структуры для отображения "технических данных"         |
|         |          | UI - UI config for user (sizing)                                   |
|         |          | Model for user UI config and API                                   |
|         |          | UI - страница переводов: hotkeys (Enter -> next translate)         |
|         |          | UI - страница переводов: Прогресс перевода для выбранного языка    |
|         |          | Translate examples: Google                                         |
|         |          | Translate examples: translates from same file (by like)            |
|         |          | Поиск по фразе (pgSQL vectors)                                     |
|         |          | Последние изменениея перевода (юзерами - без merge check)          |
|         |          | UI - OAuth2                                                        |
|         |          | OAuth2 для авторизации у гит провайдеров                           |
| 1.01.3  | 21.09.20 | Celery: Задача по расписанию для обновления файлов из репозиториев |
| 1.01.2  | 19.09.20 | Celery: Задача для выгрузки переведенной копии в репозиторий       |
| 1.01.1  | 18.09.20 | Переделан модуль для работы с Гит провайдерами                     |
| 1.01.0  | 09.09.20 | Переделан UI и добавлена система прав (PrePROD)                    |
| 0.04.0  | 08.09.20 | Система прав пользователей                                         |
| 0.04.1  | 04.09.20 | Вся бизнес логика раскидана по сервисам                            |
| 0.03.9  | 01.09.20 | Утилиты для тестирования (django commands)                         |
| 0.03.8  | 29.08.20 | Тесты для API авторизации и проектов                               |
| 0.03.7  | 25.08.20 | Управляющий модуль runner.sh для управления docker и приложением   |
| 0.03.6  | 24.08.20 | Celery: Задача по загрузке файла                                   |
| 0.03.5  | 22.08.20 | Управляющий класс для файлов, доработка services                   |
| 0.03.4  | 19.08.20 | Служебные функции в классы services                                |
| 0.03.3  | 15.08.20 | Сервера: redis, celery - настройка                                 |
| 0.03.2  | 14.08.20 | Docker - окружение dev и немного prod                              |
| 0.03.1  | 12.08.20 | Система логирования                                                |
| 0.03.0  | 05.08.20 | Перевод сервера в Docker                                           |
| 0.02.11 | 30.07.20 | Гит: обновление ссылки для папки - проверка всех файлов            |
| 0.02.10 | 28.07.20 | Гит: проверка файла, скачивание - github, bitbucket                |
| 0.02.9  | 24.07.20 | Модуль для работы с гит репозиториями                              |
| 0.02.8  | 20.07.20 | Создание переведенной копии + скачивание                           |
| 0.02.7  | 14.07.20 | Прогресс перевода файла                                            |
| 0.02.6  | 13.07.20 | Фильтрация на странице для перевода текстов                        |
| 0.02.5  | 10.07.20 | Страница для перевода текстов                                      |
| 0.02.4  | 04.07.20 | Переработка модели: метки - переводы (оригиналов нет)              |
| 0.02.3  | 26.06.20 | Парсинг файла: метод csv (доработка модели)                        |
| 0.02.2  | 24.06.20 | Парсинг файла: метод ue, html                                      |
| 0.02.1  | 20.06.20 | Модель для хранения оригиналов и переводов текста                  |
| 0.02.0  | 16.06.20 | Парсинг файла: получение информации о файле                        |
| 0.01.8  | 08.06.20 | Отображение файлов (mock data)                                     |
| 0.01.7  | 05.06.20 | Менюшки для управления проектами и папками                         |
| 0.01.6  | 03.06.20 | Загрузка файлов через браузер (DropZone)                           |
| 0.01.6  | 29.05.20 | Управление файлами и папками (API)                                 |
| 0.01.5  | 25.05.20 | Загрузка файлов (API)                                              |
| 0.01.4  | 18.05.20 | knox авторизация (по токену)                                       |
| 0.01.3  | 15.05.20 | Базовый интерфейс для управления проектами и папками               |
| 0.01.2  | 12.05.20 | API на текущую модель                                              |
| 0.01.1  | 10.05.20 | Модель приложения: языки, проекты, папки                           |

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
