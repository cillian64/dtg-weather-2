#!/bin/bash

virtualenv -p python3 venv
source venv/bin/activate
pip install gunicorn flask psycopg2 pytz

