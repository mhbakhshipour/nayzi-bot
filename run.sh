#!/bin/bash

python manage.py migrate &
python manage.py telegrambot &
python manage.py runserver
