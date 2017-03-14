import psycopg2 as pg
import pytz
from datetime import datetime

inst_sensors = {"temperature": "insttemp",
                "humidity": "insthum",
                "dewpoint": "instdewpt",
                "pressure": "instpressure",
                "windspeed": "instwindspd",
                "winddirection": "instwinddir",
                "sunshine": "instsunshine",
                "rainfall": "instrainfall"}
hist_sensors = {"temperature": "avtemp",
                "humidity": "avhum",
                "dewpoint": "avdewpt",
                "pressure": "avpressure",
                "windspeed": "avwindspd",
                "maxwindspeed": "maxwindspd",
                "winddirection": "avwinddir",
                "sunshine": "instsunhours",
                "rainfall": "instrainfall"}

def all_sensors(db, datefrom, dateto, inst, timeobj=False):
    """
    Return a dictionary of result-sets for all sensors for the
    date-range specified.  db is a psycopg2 connection object,
    datefrom and dateto are datetime objects.
    If inst is true, use few-secondly readings, if False, half-hourly
    If timeobj is True, timestamps are returned as tz-aware datetime objects
    if false, they are converted to ISO-format strings.
    Result looks like {'temp': tempdata, 'dewpt': dewptdata, ...}
    """
    sensors = inst_sensors if inst else hist_sensors

    results = dict()
    for sensor in sensors:
        results[sensor] = get_sensor(db, sensor, datefrom, dateto, inst,
                                     timeobj)
    return results

def get_sensor(db, sensor, datefrom, dateto, inst, timeobj=False):
    """
    Return a result-set for the given sensor for a date range.
    db is a psycopg2 database connection object, datefrom and
    dateto are datetime objects.
    If inst is true, use few-secondly readings, if False, half-hourly
    Result looks like [(t0, val0), (t1, val1), (t2, val2), ...]
    """
    if ((not isinstance(datefrom, datetime)) or
        (not isinstance(dateto, datetime))):
        raise ValueError("datefrom and dateto must both be datetime objects")

    if inst:
        sensors = inst_sensors
        table = "tblWeatherInstantaneous"
    else:
        sensors = hist_sensors
        table = "tblWeatherHistoric"

    if sensor not in sensors:
        raise ValueError("Invalid sensor type '{}'".format(sensor))

    cur = db.cursor()
    # Interpret the tz-naive records as being in UTC:
    cur.execute("SET SESSION TIME ZONE 'UTC';")
    RECORD_LIMIT = 50000
    query = "SELECT timestamp, {} ".format(sensors[sensor])
    query += "FROM {} ".format(table)
    query += "WHERE timestamp BETWEEN %s and %s LIMIT %s;"
    cur.execute(query, (datefrom, dateto, RECORD_LIMIT))
    datas = cur.fetchall()
    
    converter = convert(sensors[sensor])
    # Convert all the data:
    datas = [(t, converter(d)) for (t, d) in datas]
    # Localize all the timestamps:
    datas = [(pytz.utc.localize(t), d) for (t, d) in datas]
    # If necessary convert timestamps to ISO text string:
    if not timeobj:
        datas = [(t.isoformat(), d) for (t, d) in datas]
    return datas


def convert(sensorfield):
    """
    Return a converter to convert data readings from database format to API
    format for a given sensor type.  i.e:
    data_api = convert("temp")(data_sql)
    """
    if sensorfield in ["insttemp", "avtemp", "instdewpt", "avdewpt",
                       "instwindspd", "avwindspd", "maxwindspd"]:
        return lambda data: 0.1 * data
    elif sensorfield == "instrainfall":
        return lambda data: 0.001 * data
    elif sensorfield == "instsunshine":  # From inst
        return lambda data: data/3600.0  # Stored in seconds, conv to hours
    elif sensorfield == "instsunhours":  # From hist
        return lambda data: data/100.0  # Stored in hundredths of hours
    elif sensorfield in ["instwinddir", "avwinddir", "insthum", "avhum",
                        "instpressure", "avpressure"]:
        return lambda data: data
    else:
        raise ValueError("Invalid sensor type '{}'".format(sensorfield))

