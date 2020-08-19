#!/bin/bash
MYCUSTOMTAB='   '
clear
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
    if [ $1 -eq 1 ]; then
        echo "${MYCUSTOMTAB}Django srv options..."
    elif [ $1 -eq 2 ]; then
        echo "${MYCUSTOMTAB}Display logs..."
    elif [ $1 -eq 3 ]; then
        echo "${MYCUSTOMTAB}Go sh..."
    else
        echo "${MYCUSTOMTAB}Second parameter ignored"
    fi
    selected=$1
    selected2=$2
else
    echo_line
    echo "${MYCUSTOMTAB}1 - options with django srv (django)"
    echo "${MYCUSTOMTAB}2 - display logs (srv select)"
    echo "${MYCUSTOMTAB}3 - sh command line (srv select)"
    echo "${MYCUSTOMTAB}5 - build and run server (all)"
    echo "${MYCUSTOMTAB}6 - down srvs without vols (all)"
    echo "${MYCUSTOMTAB}7 - start prod server (all)"
    echo "${MYCUSTOMTAB}9 - clear unused data and images (images)"
    echo "${MYCUSTOMTAB}0 - !!! clear all data and images !!! (images)"
    echo "${MYCUSTOMTAB}* - rebuild and restart (all & vols)"
    echo_line
    read -p "Select option to do: " option
    selected=$option
fi

echo_line
case "$selected" in

    1)  if [ -z "$selected2" ]; then
            echo "${MYCUSTOMTAB}1 - create superuser"
            echo "${MYCUSTOMTAB}2 - development tests"
            echo "${MYCUSTOMTAB}5 - production tests"
            echo "${MYCUSTOMTAB}* - make migrations and migrate"
            echo_line
            read -p "Select action for django srv: " log_option
            selected2=$log_option
        fi
        case "$selected2" in
            1) docker-compose run --rm django sh -c "python manage.py createsuperuser" ;;
            2) docker-compose run --rm django sh -c "python manage.py test" ;;
            5) docker-compose -f docker-compose.prod.yml run --rm django sh -c "python manage.py test" ;;
            *)  docker-compose run --rm django sh -c "python manage.py makemigrations"
                docker-compose run --rm django sh -c "python manage.py migrate" ;;
        esac ;;

    2)  if [ -z "$selected2" ]; then
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
    3)  if [ -z "$selected2" ]; then
            echo_servers
            read -p "Select srv to go command line for: " option2
            selected2=$option2
        fi
        case "$selected2" in
            1) docker-compose exec react sh ;;
            2) docker-compose exec celery sh ;;
            3) docker-compose exec redis sh ;;
            4) docker-compose exec postgres sh ;;
            *) docker-compose exec django sh ;;
        esac ;;
    5) docker-compose up -d --build ;;
    6) docker-compose down ;;
    7)  docker-compose -f docker-compose.prod.yml down -v 
        docker-compose -f docker-compose.prod.yml up -d --build ;;
    9)  docker-compose up -d --build
        docker system prune -a --volumes ;;
    0)  docker-compose down -v
        docker system prune -a -f --volumes ;;
    *)  docker-compose down
        docker-compose up -d --build ;;
esac
