#! /bin/bash
export $(cat .env | grep -v ^# | xargs) &&
    python manage.py graph_models -a -g -o db_layout_`date +%d-%m-%Y`.png
