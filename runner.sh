#!/bin/bash
MYCUSTOMTAB='   '
echo "====================================="
echo "${MYCUSTOMTAB}-= Abyss localize manager =-"

if [ "$#" -eq 1 ]; then
    echo "====================================="
    echo "${MYCUSTOMTAB}Option selected: $1"
    selected=$1
elif [ "$#" -eq 2 ] && [ $1 -eq 3 ]; then
    echo "====================================="
    echo "${MYCUSTOMTAB}Display logs..."
    echo "====================================="
    selected=3
    selected2=$2
else
    echo "====================================="
    echo "${MYCUSTOMTAB}1 - make migrations and migrate"
    echo "${MYCUSTOMTAB}2 - create superuser"
    echo "${MYCUSTOMTAB}3 - display logs"
    echo "${MYCUSTOMTAB}5 - build and run server"
    echo "${MYCUSTOMTAB}0 - down server and volumes"
    echo "${MYCUSTOMTAB}* - rebuild"
    echo "====================================="
    read -p "Select option to do: " option
    selected=$option
fi

case "$selected" in
    1) docker-compose run --rm django sh -c "python manage.py makemigrations"
       docker-compose run --rm django sh -c "python manage.py migrate" ;;
    2) docker-compose run --rm django sh -c "python manage.py createsuperuser" ;;
    3)  if [ -z "$selected2" ]; then
            echo "====================================="
            echo "${MYCUSTOMTAB}1 - react"
            echo "${MYCUSTOMTAB}2 - celery"
            echo "${MYCUSTOMTAB}3 - redis"
            echo "${MYCUSTOMTAB}4 - postgres"
            echo "${MYCUSTOMTAB}* - django"
            echo "====================================="
            read -p "Select srv to display logs for: " log_option
            selected2=$log_option
        fi

        case "$selected2" in
            1) docker-compose logs react ;;
            2) docker-compose logs celery ;;
            3) docker-compose logs redis ;;
            3) docker-compose logs postgres ;;
            *) docker-compose logs django ;;
        esac ;;
    5) docker-compose up -d --build ;;
    0) docker-compose down -v ;;
    *) docker-compose down && docker-compose up -d --build ;;
esac
