#!/usr/bin/python3

import flask
from flask import Flask
from flask import jsonify
import json
import numpy as np
import os
import psycopg2
from datetime import datetime
from datetime import timedelta
app = Flask(__name__)

debug = True

CONN_STR = "host=/tmp"
conn = psycopg2.connect(CONN_STR)
conn.autocommit = True
cur = conn.cursor()

RECORD_LIMIT = 10000


def get_data(cursor, fields=[], datefrom=None, dateto=None,
             instantaneous=False):
    """
    Pass me a list of field names and a date range, and I'll fetch some data.
    I'll also include the timestamp, converted to javascript epoch format.  If
    you want data from the instantaneous table, pass instantaneous=True.  I'll
    execute the query on the cursor you passed, then return the same cursor.
    datefrom and dateto should both be python datetime objects, if passed.
    """
    if instantaneous:
        table = "tblWeatherInstantaneous"
    else:
        table = "tblWeatherHistoric"

    query = "SELECT 1000*extract(epoch from timestamp)"  # js epoch format
    query = ",".join([query] + fields)  # Append any supplied fields to get.
    query += " FROM " + table

    if not datefrom:  # Default datefrom is 24 hours ago
        datefrom = datetime.now() - timedelta(days=1)
    if not dateto:  # Default dateto is now
        dateto = datetime.now()
    query += " WHERE timestamp > %s and timestamp < %s LIMIT %s;"
    cursor.execute(query, (datefrom, dateto, RECORD_LIMIT))


@app.route("/daily.json")
def daily_everything():
    """
    All sensor readings for the past 24 hours
    """
    return get_everything(None, None)  # Default period is past 24 hrs.


def get_everything(datefrom, dateto):
    """
    All sensor readings for the defined period as a big JSON gob.
    """
    get_data(cur, ["avtemp", "avdewpt", "avwinddir", "instrainfall", "avhum",
                   "instsunhours", "avwindspd", "maxwindspd", "avpressure"],
             datefrom, dateto)
    results = cur.fetchall()
    if results:  # Did we get any results?
        # Re-zip from record-format to a set of lists:
        (t, temp, dewpt, winddir, rainfall, hum, sunhours, avwindspd,
            maxwindspd, pressure) = zip(*results)
    else:  # If not, blank results lists
        (t, temp, dewpt, winddir, rainfall, hum, sunhours, avwindspd,
            maxwindspd, pressure) = ([],)*10

    # Do necessary format conversions:
    temp = [tempconv(x) for x in temp]
    dewpt = [tempconv(x) for x in dewpt]  # Just a temperature in the db
    rainfall = [rainfallconv(x) for x in rainfall]
    avwindspd = [windconv(x) for x in avwindspd]
    maxwindspd = [windconv(x) for x in maxwindspd]

    # MicroPolar isn't so keen on proper time series plotting, so we have to
    # manually make time labels:
    twinddir = [(x - min(t))/3600000.0 for x in t]

    # JSONify a big dictionary: (we can pick it apart later in js)
    # MicroPolar doesn't like its datapoints zipped :-(
    results = {"temp":          list(zip(t, temp)),
               "dewpt":         list(zip(t, dewpt)),
               "winddir":       {"rs": twinddir, "ts": winddir},
               "rainfall":      list(zip(t, rainfall)),
               "hum":           list(zip(t, hum)),
               "sunhours":      list(zip(t, sunhours)),
               "avwindspd":     list(zip(t, avwindspd)),
               "maxwindspd":    list(zip(t, maxwindspd)),
               "pressure":      list(zip(t, pressure))}
    return jsonify(results)


def tempconv(raw):
    return 0.1*raw


def rainfallconv(raw):
    return 0.001*raw


def windconv(raw):
    return 0.1*raw


@app.route("/")
def home_redir():
    return flask.redirect('/static/today.html')

if __name__ == "__main__":
    if debug:
        print("******* DANGER ***********")
        print("DANGER! Running in debug mode, this is UNSAFE in production")
        print("******* DANGER ***********")
    app.run(debug=debug)
