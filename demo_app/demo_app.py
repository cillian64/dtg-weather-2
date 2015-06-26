import psycopg2 as pg
from flask import Flask, g
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


@application.route('/')
def hello():
    cur = g.db.cursor()
    cur.execute("""SELECT insttemp FROM tblweatherinstantaneous
                   ORDER BY timestamp DESC LIMIT 1;""")
    temperature = cur.fetchall()[0][0] / 10.0
    string = "<b>Hello, world!</b> "
    string += "The current temperature is {} celsius.".format(temperature)
    return string

if __name__ == "__main__":
    application.run(host="0.0.0.0")

