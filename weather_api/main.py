import psycopg2 as pg

import graphs
import tabulate
import currentobs
from utils import input_date
from datetime import datetime, timedelta

from flask import Flask, g, request, json, make_response, render_template
application = Flask(__name__)
DB_STR = "dbname=weather user=weather_ro host=localhost"

####### Database boilerplate
@application.before_request
def before_request():
    g.db = pg.connect(DB_STR)

@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

######## Graphs
@application.route('/weather_api/daily_graph.png', methods=['GET'])
def daily_graph():
    return graphs.daily_graph(request.args.get('date'),
                              request.args.get('sensor'))

@application.route('/weather_api/daily-graph.html', methods=['GET'])
def daily_graph_page():
    date = input_date(request.args.get('date'))
    yesterday = date - timedelta(hours=24)
    tomorrow = date + timedelta(hours=24)

    date = date.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d')
    tomorrow = tomorrow.strftime('%Y-%m-%d')
    
    return render_template('daily-graph.html', date=date, yesterday=yesterday,
                           tomorrow=tomorrow)

######### JSON
@application.route('/weather_api/all_sensors_instant.json', methods=['GET'])
def all_sensors_instant():
    return tabulate.all_sensors_instant(request.args.get('datefrom'),
                                        request.args.get('dateto'))

@application.route('/weather_api/all_sensors_historic.json', methods=['GET'])
def all_sensors_historic():
    return tabulate.all_sensors_historic(request.args.get('datefrom'),
                                         request.args.get('dateto'))

########### Tabulated
@application.route('/weather_api/daily-text.txt')
def daily_text():
    return tabulate.daily_text(request.args.get('date'))

@application.route('/weather_api/current_obs.txt')
def current_obs():
    return currentobs.current_obs()

if __name__ == "__main__":
    application.run(host="127.0.0.1")
