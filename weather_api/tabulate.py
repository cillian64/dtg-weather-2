import get_data
from utils import input_datetime, input_date

from flask import Flask, g, request, json, make_response


def all_sensors_instant(datefrom, dateto):
    datefrom = input_datetime(datefrom)
    dateto = input_datetime(dateto)
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=True)
    return json.jsonify(results)


def all_sensors_historic(datefrom, dateto):
    datefrom = input_datetime(datefrom)
    dateto = input_datetime(dateto)
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=False)
    return json.jsonify(results)
