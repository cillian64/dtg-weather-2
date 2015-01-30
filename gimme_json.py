#!/usr/bin/python3

from flask import Flask
from flask import jsonify
import json
import numpy as np
import os
import psycopg2
app = Flask(__name__)

debug = True

CONN_STR = "host=/tmp"
conn = psycopg2.connect(CONN_STR)
cur = conn.cursor()


def get_daily_cols(cursor, cols, table="tblWeatherHistoric"):
    """
    Pass me a column or comma-separated list of columns, and I'll execute the
    appropriate query to fetch appropriate data with corrected javascript-epoch
    timestamp!  By default I use tblweatherhistoric -- if you want
    instantaneous data, pass a non-default table.
    I return the same cursor you passed.
    """
    # Unfortunately psycopg2's parameterisation doesn't work for table name or
    # field names, so we have to do this with string formatting.  THIS MEANS
    # COLS AND TABLE CANNOT BE USER-FACING VARIABLES!
    cur.execute("""SELECT 1000*extract(epoch from timestamp),{}
                   FROM {}
                   WHERE timestamp > (now() - INTERVAL '1 day');""".format(
                   cols, table))


@app.route("/daily_temperature.json")
def daily_temperature():
    get_daily_cols(cur, "avtemp")
    results = [(x, 0.1*y) for (x,y) in cur.fetchall()]
    return jsonify({'results': results})


@app.route("/daily_dewpoint.json")
def daily_dewpoint():
    get_daily_cols(cur, "avdewpt")
    return jsonify({'results': cur.fetchall()})


@app.route("/daily_winddir.json")
def daily_winddir(): # rs=radius=time, ts=theta=direction
    get_daily_cols(cur, "avwinddir")
    rs, ts = zip(*cur.fetchall())
    # MicroPolar doesn't handle javascript times properly, so we'll convert
    # js timestamps to sensible numbers:
    rs = [(r - min(rs))/3600000.0 for r in rs]
    return jsonify({'rs': rs, 'ts': ts})


@app.route("/daily_rainfall.json")
def daily_rainfall():
    get_daily_cols(cur, "instrainfall")
    results = [(x, 0.001*y) for (x,y) in cur.fetchall()]
    return jsonify({'results': results})


@app.route("/daily_humidity.json")
def daily_humidity():
    get_daily_cols(cur, "avhum")
    return jsonify({'results': cur.fetchall()})


@app.route("/daily_sunshine.json")
def daily_sunshine():
    get_daily_cols(cur, "instsunhours")
    return jsonify({'results': cur.fetchall()})


@app.route("/daily_windspeed.json")
def daily_windspeed():
    get_daily_cols(cur, "avwindspd, maxwindspd")
    ts, avs, maxs = zip(*cur.fetchall())
    avs = [0.1*x for x in avs]
    maxs = [0.1*x for x in maxs]
    results = [list(zip(ts, avs)), list(zip(ts, maxs))]
    return jsonify({'results': results})


@app.route("/daily_pressure.json")
def daily_pressure():
    get_daily_cols(cur, "avpressure")
    return jsonify({'results': cur.fetchall()})


if __name__ == "__main__":
    if debug:
        print("******* DANGER ***********")
        print("DANGER! Running in debug mode, this is UNSAFE in production")
        print("******* DANGER ***********")
    app.run(debug=debug)
