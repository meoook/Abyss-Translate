#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "No param or empty"
    exit 1
else
    echo "Param is $1"
    exit 1
fi

if [ -z "$1" ]
then
    echo "================================"
    echo "1 - make migrations and migrate"
    echo "2 - create superuser"
    echo "3 - display logs"
    echo "0 - server and volumes down"
    echo "default - rebuild"
    echo "================================"

    read -p "Select option to do: " option
    selected=$option
else
    echo "\$1 not empty"
    selected=$1
fi

case "$selected" in
    1) docker-compose run --rm django sh -c "python manage.py makemigrations"
       docker-compose run --rm django sh -c "python manage.py migrate" ;;
    2) docker-compose run --rm django sh -c "python manage.py createsuperuser" ;;
    3) 
        echo "================================"
        echo "1 - react"
        echo "2 - celery"
        echo "3 - redis"
        echo "4 - postgres"
        echo "default - django"
        echo "================================"
        read -p "Select srv to display logs for: " log_option

        case "$log_option" in
            1) docker-compose logs react ;;
            2) docker-compose logs celery ;;
            3) docker-compose logs redis ;;
            3) docker-compose logs postgres ;;
            *) docker-compose logs django ;;
        esac
     ;;
    0) docker-compose down -v ;;
    *) docker-compose down && docker-compose up -d --build ;;
esac
