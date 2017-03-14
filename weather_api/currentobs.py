import psycopg2 as pg

from flask import Flask, g, request, json, make_response
from get_data import convert

from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone

from utils import winddir

def executive_summary(sun, rain, hum, temp, wind):
    summary = []

    if sun > 0:
        summary.append("sunny")

    if rain > 0:
        summary.append("rainy")
    else:
        if hum < 15:
            summary.append("very dry")
        elif hum < 30:
            summary.append("dry")
        elif hum > 70 and hum < 85:
            summary.append("humid")
        elif hum > 85:
            summary.append("very humid")

    if temp <= 0:
        summary.append("freezing cold")
    elif temp <= 4:
        summary.append("very cold")
    elif temp <= 9:
        summary.append("cold")
    elif temp <= 13:
        summary.append("cool")
    elif temp <= 18:
        summary.append("mild")
    elif temp <= 23:
        summary.append("warm")
    elif temp <= 27:
        summary.append("hot")
    else:
        summary.append("very hot")

    if wind <= 0:
        summary.append("calm")
    elif wind <= 4:
        summary.append("light winds")
    elif wind <= 10:
        summary.append("windy")
    elif wind <= 20:
        summary.append("very windy")
    else:
        summary.append("extremely windy")

    return summary
    

def current_obs():
    cur = g.db.cursor()
    cur.execute("SET SESSION TIME ZONE 'UTC';")
    cur.execute("""SELECT timestamp, insttemp, instpressure, insthum,
                   instdewpt, instwindspd, instwinddir, instsunshine,
                   instrainfall
                   FROM tblWeatherInstantaneous
                   ORDER BY timestamp DESC LIMIT 1;""")
    row = cur.fetchone()
    
    # Time comes out of DB as naive UTC time. Localise to UTC:
    dbnow = pytz.utc.localize(row[0])
    # Find out system local tz and convert dbtime from utc to local time:
    local_now = dbnow.astimezone(get_localzone())
    # Convert to legacy format:
    date = local_now.strftime("%d %b %y")
    time = local_now.strftime("%I:%M %p")
    out = ("Cambridge Computer Laboratory Rooftop Weather at {} on {}:\n\n"
           "".format(time, date))

    # Retrieve readings from database row:
    temp = convert("insttemp")(row[1])
    pressure = convert("instpressure")(row[2])
    humidity = convert("insthum")(row[3])
    dewpt = convert("instdewpt")(row[4])
    windspd = convert("instwindspd")(row[5])
    wind_from = winddir(row[6])
    sun = row[7]
    rain = row[8]

    # Each instantaneous readings from the database:
    out += "Temperature:  {:.1f} C\n".format(temp)
    out += "Pressure:     {} mBar\n".format(pressure)
    out += "Humidity:     {} %\n".format(humidity)
    out += "Dewpoint:     {:.1f} C\n".format(dewpt)
    out += "Wind:         {:.0f} knots".format(windspd)
    out += " from the {}\n".format(wind_from)

    # Let's add up sun and rain since midnight:
    now = datetime.utcnow()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    cur.execute("""SELECT sum(instsunshine), sum(instrainfall)
                   FROM tblWeatherInstantaneous
                   WHERE timestamp > %s;""", (midnight,))
    row = cur.fetchone()
    out += "Sunshine:     {:.1f} hours (today)\n".format(
        convert("instsunshine")(row[0]))
    out += "Rainfall:     {:.1f} mm since midnight\n\n".format(
        convert("instrainfall")(row[1]))

    # Generate the executive summary:
    summary = executive_summary(sun, rain, humidity, temp, windspd)
    out += "Summary:      {}\n".format(", ".join(summary))

    response = make_response(out)
    response.mimetype = "text/plain"
    return response

