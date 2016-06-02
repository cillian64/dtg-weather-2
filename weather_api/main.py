import get_data
import psycopg2 as pg
from datetime import datetime, timedelta
import pytz

from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from numpy import arange

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

def input_datetime(string):
    """
    Handles an ISO-format input date string in UTC only, format like
    YY-MM-DDTHH:MM:SSZ or YY-MM-DDTHH:MM:SS+00:00
    Returns a timezone-aware UTC datetime object.
    """
    if string[-1] == 'Z':
        conv = datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
    elif string[-6:] == "+00:00":
        conv = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S+00:00")
    else:
        raise ValueError("Invalid string TZ type in {}".format(string))

    tz = pytz.timezone('UTC')
    return tz.localize(conv)

def input_date(string):
    """
    Handles an ISO-format date string, format like YY-MM-DD
    Returns a timezone-aware UTC datetime object of midnight on that day.
    """
    conv = datetime.strptime(string, "%Y-%m-%d")

    tz = pytz.timezone('UTC')
    return tz.localize(conv)

@application.route('/weather_api/daily_graph.png', methods=['GET'])
def daily_graph():
    print(request.args.get('date'))
    datefrom = input_date(request.args.get('date'))
    sensor = request.args.get('sensor')
    dateto = datefrom + timedelta(hours=24) 
    results = get_data.get_sensor(g.db, sensor, datefrom, dateto,
                                  inst=False)
    xs, ys = zip(*results)
    xs = [input_datetime(x) for x in xs]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    if sensor == 'temperature' or sensor == 'dewpoint':
        axis.set_ylim((-10, 35))
    elif sensor == 'humidity':
        axis.set_ylim((0, 100))
    elif sensor == 'pressure':
        axis.set_ylim((970, 1050))
    elif sensor == 'rainfall':
        axis.set_ylim((0, 10))
    elif sensor == 'sunshine':
        axis.set_ylim((0, 1))
    elif sensor == 'windspeed':
        axis.set_ylim((0, 70))
    axis.xaxis.set_major_locator(HourLocator(arange(0, 25, 6)))
    axis.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    axis.plot(xs, ys)

    if sensor == 'windspeed':
        maxes = get_data.get_sensor(g.db, "maxwindspeed", datefrom, dateto,
                                    inst=False)
        xs, ys = zip(*maxes)
        xs = [input_datetime(x) for x in xs]
        axis.plot(xs, ys)

    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@application.route('/weather_api/all_sensors_instant', methods=['GET'])
def all_sensors_instant():
    datefrom = input_datetime(request.args.get('datefrom'))
    dateto = input_datetime(request.args.get('dateto'))
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=True)
    return json.jsonify(results)


@application.route('/weather_api/all_sensors_historic', methods=['GET'])
def all_sensors_historic():
    datefrom = input_datetime(request.args.get('datefrom'))
    dateto = input_datetime(request.args.get('dateto'))
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=False)
    return json.jsonify(results)


if __name__ == "__main__":
    application.run(host="127.0.0.1")
