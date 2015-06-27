#!/usr/bin/python3

import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

from datetime import datetime
from datetime import timedelta

import data_retrieval

app = Flask(__name__)

#debug = False
debug = True  # This option is unsafe in production.  It allows trivial
              # access to remote execution.



@app.route("/daily.json")
def daily_everything():
    """
    All sensor readings for the past 24 hours
    """
    return data_retrieval.get_everything()  # Default period is past 24 hrs.


@app.route("/daterange.json", methods=['GET'])
def get_daterange():
    """
    All sensor readings for the defined period as a big JSON gob.
    """
    
    datefrom = request.args.get('datefrom')
    dateto = request.args.get('dateto')

    return data_retrieval.get_everything(datefrom, dateto)


@app.route("/")
def home_redir():
    return flask.redirect('/static/today.html')


if __name__ == "__main__":
    if debug:
        print("******* DANGER ***********")
        print("DANGER! Running in debug mode, this is UNSAFE in production")
        print("******* DANGER ***********")
    app.run(debug=debug)
