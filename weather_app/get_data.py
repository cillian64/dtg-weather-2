import psycopg2 as pg

inst_sensors = ["temp", "hum", "dewpt", "pressure", "windspd", "winddir",
                "sunshine", "rainfall"]
hist_sensors = []

def all_sensors(db, datefrom, dateto, inst):
    """
    Return a dictionary of result-sets for all sensors for the
    date-range specified.  db is a psycopg2 connection object,
    datefrom and dateto are datetime objects.
    If inst is true, use few-secondly readings, if False, half-hourly
    Result looks like {'temp': tempdata, 'dewpt': dewptdata, ...}
    """
    if not inst:
        raise NotImplementedError
    sensors = inst_sensors if inst else hist_sensors

    results = dict()
    for sensor in sensors:
        results[sensor] = get_sensor(db, sensor, datefrom, dateto, inst)
    return results

def get_sensor(db, sensor, datefrom, dateto, inst):
    """
    Return a result-set for the given sensor for a date range.
    db is a psycopg2 database connection object, datefrom and
    dateto are datetime objects.
    If inst is true, use few-secondly readings, if False, half-hourly
    Result looks like [(t0, val0), (t1, val1), (t2, val2), ...]
    """
    if datefrom is None or dateto is None:
        raise ValueError("datefrom and dateto must both be specified")

    sensors = inst_sensors if inst else hist_sensors
    if not inst:
        raise NotImplementedError

    if sensor not in sensors:
        raise ValueError("Invalid sensor type '{}'".format(sensor))

    cur = db.cursor()
    RECORD_LIMIT = 50000
    query = "SELECT timestamp, {} ".format("inst" + sensor)
    query += "FROM tblWeatherInstantaneous "
    query += "WHERE timestamp BETWEEN %s and %s LIMIT %s"
    cur.execute(query, (datefrom, dateto, RECORD_LIMIT))
    
    converter = convert(sensor)
    return [(t, converter(data)) for (t, data) in cur]


def convert(sensor):
    """
    Return a converter to convert data readings from database format to API
    format for a given sensor type.  i.e:
    data_api = convert("temp")(data_sql)
    """
    if sensor in ["temp", "dewpt", "windspd"]:
        return lambda data: 0.1 * data
    elif sensor == "rainfall":
        return lambda data: 0.001 * data
    elif sensor in ["winddir", "hum", "sunshine", "pressure"]:
        return lambda data: data
    else:
        raise ValueError("Invalid sensor type '{}'".format(sensor))

