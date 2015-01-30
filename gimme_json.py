#!/usr/bin/python3

from flask import Flask
from flask import jsonify
import json
import numpy as np
import os
import psycopg2
app = Flask(__name__)

CONN_STR = "host=/tmp"

@app.route("/gimme.json")
def gimme_json():
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("""SELECT 1000*extract(epoch from timestamp), insttemp
                 FROM tblweatherhistoric
                 WHERE timestamp > (now() - INTERVAL '1 day');""")
    results = [(x, 0.1*y) for (x,y) in cur.fetchall()]
    return jsonify({'results': results})
   
@app.route("/wind.json")
def wind_json():
    xs = np.linspace(0, 2*np.pi, 100)
    ys = np.sin(xs) + 1
    return jsonify({'xs': list(xs*180/np.pi), 'ys': list(ys)})

@app.route("/test.json")
def test_json():
    xs = np.linspace(0, 2*np.pi, 100)
    ys = np.sin(xs)
    return jsonify({'results': list(zip(list(xs), list(ys)))})


if __name__ == "__main__":
    print("******* DANGER ***********")
    print("DANGER! Running in debug mode, this is NOT SAFE in production")
    print("******* DANGER ***********")
    app.run(debug=True)
