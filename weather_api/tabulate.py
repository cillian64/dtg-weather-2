import get_data
from utils import input_datetime, input_date, winddir
from datetime import datetime, timedelta

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

def daily_text(date):
    datefrom = input_date(date)
    dateto = datefrom + timedelta(hours=23, minutes=59)
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=False,
                                   timeobj=True)
    # Assume all sensors have the same timestamps!
    timestamps, _ = zip(*results["temperature"])

    out = """# DTG Weather on Thursday 02 June 2016.
#
# Data are immediate at "Time" except wind speed (average since previous "Time")
# and wind direction (most frequent since previous "Time".)  Sun and rain values
# are cumulative from "Start".  MxWSpd gives max wind speed since previous "Time".
#
#Time	Temp	Humid	DewPt	Press	WindSp	WindDr	Sun  	Rain	Start	MxWSpd
#    	deg C	%    	deg C	mBar 	knots 	      	hours	mm  	     	knots
"""
    for idx, timestamp in enumerate(timestamps):
        out += timestamp.strftime("%H:%M\t")
        out += "{:.1f}\t".format(results['temperature'][idx][1])
        out += "{:.0f}\t".format(results['humidity'][idx][1])
        out += "{:.1f}\t".format(results['dewpoint'][idx][1])
        out += "{:.0f}\t".format(results['pressure'][idx][1])
        out += "{:.1f}\t".format(results['windspeed'][idx][1])
        out += "{}\t".format(winddir(results['winddirection'][idx][1]))
        
        # Sun and rain are cumulative
        sumsun = sum(x[1] for x in results['sunshine'][:idx+1])
        out += "{:.2f}\t".format(sumsun)
        sumrain = sum(x[1] for x in results['rainfall'][:idx+1])
        out += "{:.2f}\t".format(sumrain)

        # Legacy "Start" time is always midnight:
        out += "00:00\t"

        # Cumulative max wind speed:
        maxwind = max(x[1] for x in results['maxwindspeed'][:idx+1])
        out += "{:.0f}".format(results['maxwindspeed'][idx][1])

        out += "\n"

    response = make_response(out)
    response.mimetype = "text/plain"
    return response
