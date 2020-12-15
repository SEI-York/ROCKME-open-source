#!/bin/bash
#----------

# Source the dev environment and kick off the app $1 is an optional port to listen on
export $(cat .env | grep -v ^# | xargs) && python manage.py runserver "$1"
