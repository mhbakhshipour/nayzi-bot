#!/bin/bash

python manage.py migrate &
python manage.py runserver &
python manage.py telegrambot
