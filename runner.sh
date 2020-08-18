#!/bin/bash
MYCUSTOMTAB='   '

function echo_line {
    echo "====================================="
}

function echo_servers {
    echo "${MYCUSTOMTAB}1 - react"
    echo "${MYCUSTOMTAB}2 - celery"
    echo "${MYCUSTOMTAB}3 - redis"
    echo "${MYCUSTOMTAB}4 - postgres"
    echo "${MYCUSTOMTAB}* - django"
    echo_line
}

echo_line
echo "${MYCUSTOMTAB}- Abyss Localize Manager -"

if [ "$#" -eq 1 ]; then
    echo_line
    echo "${MYCUSTOMTAB}Option selected: $1"
    selected=$1
elif [ "$#" -eq 2 ]; then
    echo_line
    if [ $1 -eq 3 ]; then
        echo "${MYCUSTOMTAB}Display logs..."
    elif [ $1 -eq 4 ]; then
        echo "${MYCUSTOMTAB}Go sh..."
    else
        echo "${MYCUSTOMTAB}Second parameter ignored"
    fi
    selected=$1
    selected2=$2
else
    echo_line
    echo "${MYCUSTOMTAB}1 - make migrations and migrate (django)"
    echo "${MYCUSTOMTAB}2 - create superuser (django)"
    echo "${MYCUSTOMTAB}3 - display logs (srv select)"
    echo "${MYCUSTOMTAB}4 - sh command line (srv select)"
    echo "${MYCUSTOMTAB}5 - build and run server (all)"
    echo "${MYCUSTOMTAB}0 - down server and volumes (all & vols)"
    echo "${MYCUSTOMTAB}* - rebuild and start"
    echo_line
    read -p "Select option to do: " option
    selected=$option
fi

echo_line
case "$selected" in
    1) docker-compose run --rm django sh -c "python manage.py makemigrations"
       docker-compose run --rm django sh -c "python manage.py migrate" ;;
    2) docker-compose run --rm django sh -c "python manage.py createsuperuser" ;;
    3)  if [ -z "$selected2" ]; then
            echo_servers
            read -p "Select srv to display logs for: " log_option
            selected2=$log_option
        fi
        case "$selected2" in
            1) docker-compose logs -f react ;;
            2) docker-compose logs -f celery ;;
            3) docker-compose logs -f redis ;;
            3) docker-compose logs -f postgres ;;
            *) docker-compose logs -f django ;;
        esac ;;
    4)  if [ -z "$selected2" ]; then
            echo_servers
            read -p "Select srv to go command line for: " option2
            selected2=$option2
        fi
        case "$selected2" in
            1) docker-compose exec react sh ;;
            2) docker-compose exec celery sh ;;
            3) docker-compose exec redis sh ;;
            3) docker-compose exec postgres sh ;;
            *) docker-compose exec django sh ;;
        esac ;;
    5) docker-compose up -d --build ;;
    0) docker-compose down -v ;;
    *) docker-compose down && docker-compose up -d --build ;;
esac

echo_line
