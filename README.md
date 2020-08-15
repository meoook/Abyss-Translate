# Abyss-Translate (Localize)

Сервис локализации игровых файлов. Позволяет загружать
файлы игр для локализации, оставляя для переводчика только
**"полезный текст"**, отсекая "технические данные".
Работает с гит репозиториями: **github, bitbucket, gitlab**

### Зависимости

Для работы приложения необходим **_Docker v3.7_**
<code>
apt-get install -y docker
</code>
и **_Docker-Compose v3.7_**
<code>
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
docker-compose version 1.26.2, build 1110ad01
</code>
<warning>
For alpine, the following dependency packages are needed: py-pip, python-dev, libffi-dev, openssl-dev, gcc, libc-dev, and make.
</warning>

## Diamond 💎 5%

## Gold 🏆 12%

<code>
    gunicorn --bind :8000 --workers 3 mysite.wsgi:application
</code>
