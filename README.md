# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации, оставляя для переводчика только
**_полезный текст_**, отсекая _технические данные_.

###### version: 0.2

###### author: meok

Реализованы функции:

- [x] загрузка файла (API)
- [x] автоматический парсинг файла (**html**, **csv**, **po**)
- [x] создание переведенных копий и их выгрузка через API
- [ ] роли пользователей и проверки
- [x] работа с гит репозиториями (API)
- [x] расписание задач
- [x] логирование
- [ ] ручная обработка файла

# Поддержка гит провайдеров:

- [x] **github**
- [x] **bitbucket**
- [ ] **gitlab**

## Зависимости

Для работы приложения необходим **Docker v3.7**

```sh
$ apt-get install -y docker
```

и **Docker-Compose v1.26.2**

```sh
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
docker-compose version 1.26.2, build 1110ad01
```

> For alpine, the following dependency packages are needed:
> `py-pip, python-dev, libffi-dev, openssl-dev, gcc, libc-dev, and make.`

## Запуск приложения

```sh
$ docker-compose up -d --build
```

или

```sh
$ sh runner.sh 5
```

## Diamond 💎 5%

| Название файла | Содержание файла                     |
| -------------- | ------------------------------------ |
| style.css      | Пустой файл каскадной таблицы стилей |
| reset.css      | Reset CSS от Эрика Мейера            |
| normalize.css  | Нормалайзер CSS от Nicolas Gallagher |
| block.css      | Основные стили блоков системы        |

## Gold 🏆 12%

`gunicorn --bind :8000 --workers 3 mysite.wsgi:application`

Для форматирования текста на GitHub используются достаточно простые правила. Я перечислю основные и достаточные, так как не претендую на полноту официального руководства.

---

Текст можно обработать в любом простом текстовом редакторе, например в Notepad++, которым пользуюсь сам. А можно и прямо на GitHub редактировать файл в он-лайн режиме.

---

Стилистическая разметка должна быть так :+1:

## Заданя по расписанию
