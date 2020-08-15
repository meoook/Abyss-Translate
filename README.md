# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации,
оставляя для переводчика только
**"полезный текст"**, отсекая "технические данные".
Работает с гит репозиториями:

- **github**
- **bitbucket**
- **gitlab**

### Зависимости

Для работы приложения необходим **_Docker v3.7_**

```
apt-get install -y docker
```

и `Docker-Compose v3.7`

```sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
docker-compose version 1.26.2, build 1110ad01
```

<warning>
For alpine, the following dependency packages are needed: py-pip, python-dev, libffi-dev, openssl-dev, gcc, libc-dev, and make.
</warning>

## Diamond 💎 5%

| Название файла | Содержание файла                                                                      |
| -------------- | ------------------------------------------------------------------------------------- |
| style.css      | Пустой файл каскадной таблицы стилей, в который производится сбока необходимых стилей |
| reset.css      | Reset CSS от Эрика Мейера                                                             |
| normalize.css  | Нормалайзер CSS от Nicolas Gallagher                                                  |
| block.css      | Основные стили блоков системы                                                         |

## Gold 🏆 12%

<code>
    gunicorn --bind :8000 --workers 3 mysite.wsgi:application
</code>

Для форматирования текста на GitHub используются достаточно простые правила. Я перечислю основные и достаточные, так как не претендую на полноту официального руководства.

---

Текст можно обработать в любом простом текстовом редакторе, например в Notepad++, которым пользуюсь сам. А можно и прямо на GitHub редактировать файл в он-лайн режиме.

---

Стилистическая разметка должна быть так
