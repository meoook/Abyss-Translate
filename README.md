# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации, оставляя для переводчика только
**_полезный текст_**, отсекая _технические данные_.

* prod site: [localize.ru][prod]
* pre prod: [91.225.238.193][pre prod]
* version: 1.04.2
* author: [meok][author]
* build: react, django, postgres, celery, redis, nginx

## Функции приложения:

- [x] управление проектами(играми)
- [x] загрузка файла API (**new**, **original**, **translates**)
- [x] автоматический парсинг файла (**html**, **csv**, **po**, **row**)
- [x] парсинг загруженных переведенных копий
- [x] создание переведенных копий и их выгрузка через API
- [x] роли пользователей для проектов(игр)
- [x] авторизация с сервера abyss (JWT)
- [x] работа с гит репозиториями API (warning **bitbucket** ready only)
- [x] OAuth2 для авторизации репозиториев (**github**, **gitlab**, **bitbucket**)
- [x] расписание задач (Заданя Celery)
- [x] логирование
- [x] контроль файлов с ошибками (без админки)
- [ ] поиск похожих переводов
- [ ] база переводов
- [ ] ручная обработка файла

## Поддержка гит провайдеров:

- [x] **github**
- [x] **bitbucket** (OAuth)
- [x] **gitlab**

## Заданя Celery

- [x] T1: Обновление файла в гит репозитории (если возможно) и последующий парсинг
- [x] T2: Создание переведенной копии и размещении ее в гит репозитории (если возможно)
- [x] T3: Изменение URL репозитория для папки
- [x] T4: Изменение доступа репозитория для папки (OAuth, token, Abyss as default)
- [x] T5: Удаление файлов и папок
- [x] P1: Проверка файлов в репозиториях на обновление **by hash**
- [x] P2: Создание переведенных копий и обновление их в репозитории 

## Зависимости

Для работы приложения необходим **Docker 19.03.12**

```sh
$ apt-get install -y docker
$ docker --version
Docker version 19.03.8, build afacb8b7f0
```

а так же необходим **Docker-Compose 1.26.2**

```sh
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
docker-compose version 1.26.2, build 1110ad01
```

> For alpine, the following dependency packages are needed:
> `py-pip`, `python-dev`, `libffi-dev`, `openssl-dev`, `gcc`, `libc-dev`, and `make?`.

## Запуск приложения

После установки docker и docker-compose, выполняем из папки приложения

```sh
$ docker-compose up -d --build
```

или

```sh
$ sh ./runner.sh 5
```

## Release notes

[Release notes][log]

## Dev help page

[Dev help][dev help]

[prod]: <https://localizegame.com> "Abyss localize system"
[pre prod]: <http://91.225.238.193:3000/> "Preprod server"
[log]: <READ-LOG.md> "Release notes"
[dev help]: <READ-DEV.md> "Help for development"
[author]: <https://bazha.ru> "meok home page"