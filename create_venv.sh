#!/bin/bash

virtualenv -p python3 venv
source venv/bin/activate
cd venv/lib/python3.4/site-packages
ln -s /usr/lib/python3/dist-packages/numpy .
ln -s /usr/lib/python3/dist-packages/numpy-*.egg-info .
ln -s /usr/lib/python3/dist-packages/matplotlib .
pip install gunicorn flask psycopg2 pytz six dateutils pyparsing tzlocal
pip install Pillow
