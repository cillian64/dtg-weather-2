import get_data
from datetime import datetime, timedelta

from utils import input_datetime, input_date

from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from numpy import arange

from flask import Flask, g, request, make_response

def daily_graph(date, sensor):
    datefrom = input_date(date)
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

