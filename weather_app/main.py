import get_data
from flask import Flask, g, request, json
application = Flask(__name__)

@application.before_request
def before_request():
    g.db = pg.connect(DB_STR)


@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@application.route('/weather_app/all_sensors_instant', methods=['GET'])
def all_sensors():
    datefrom = request.args.get('datefrom')
    dateto = request.args.get('dateto')
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=True)
    return json.jsonify(results)


@application.route('/weather_app/all_sensors_historic', methods=['GET'])
def all_sensors():
    datefrom = request.args.get('datefrom')
    dateto = request.args.get('dateto')
    results = get_data.all_sensors(g.db, datefrom, dateto, inst=False)
    return json.jsonify(results)


if __name__ == "__main__":
    application.run(host="0.0.0.0")
