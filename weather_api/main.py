import get_data
import psycopg2 as pg
from datetime import datetime
import pytz
from flask import Flask, g, request, json
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


def input_date(string):
    """
    Handles an ISO-format input date string in UTC only, format like
    YY-MM-DDTHH:MM:SSZ
    Returns a timezone-aware UTC datetime object.
    """
    conv = datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
    tz = pytz.timezone('UTC')
    return tz.localize(conv)


@application.route('/weather_api/all_sensors_instant', methods=['GET'])
def all_sensors_instant():
    datefrom = input_date(request.args.get('datefrom'))
    dateto = input_date(request.args.get('dateto'))
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=True)
    return json.jsonify(results)


@application.route('/weather_api/all_sensors_historic', methods=['GET'])
def all_sensors_historic():
    datefrom = input_date(request.args.get('datefrom'))
    dateto = input_date(request.args.get('dateto'))
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=False)
    return json.jsonify(results)


if __name__ == "__main__":
    application.run(host="0.0.0.0")

