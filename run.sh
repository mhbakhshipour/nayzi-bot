#!/bin/bash

export environment=docker.env &
python manage.py migrate &
python manage.py runserver &
python manage.py telegrambot
