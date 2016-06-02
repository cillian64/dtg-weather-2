import psycopg2 as pg

import graphs
import tabulate
import currentobs

from flask import Flask, g, request, json, make_response
application = Flask(__name__)
DB_STR = "dbname=weather user=weather_ro host=localhost"

@application.before_request
def before_request():
    g.db = pg.connect(DB_STR)


@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@application.route('/weather_api/daily_graph.png', methods=['GET'])
def daily_graph():
    return graphs.daily_graph(request.args.get('date'),
                              request.args.get('sensor'))


@application.route('/weather_api/all_sensors_instant.json', methods=['GET'])
def all_sensors_instant():
    return tabulate.all_sensors_instant(request.args.get('datefrom'),
                                        request.args.get('dateto'))


@application.route('/weather_api/all_sensors_historic.json', methods=['GET'])
def all_sensors_historic():
    return tabulate.all_sensors_historic(request.args.get('datefrom'),
                                         request.args.get('dateto'))

@application.route('/weather_api/current_obs.txt')
def current_obs():
    return currentobs.current_obs()

if __name__ == "__main__":
    application.run(host="127.0.0.1")
