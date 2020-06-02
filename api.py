from flask import Flask, request, json, make_response
from decouple import config
from flask_caching import Cache
from db.mongo_db_layer import MongoDBLayer
from db.mysql_db_layer import MySqlDBLayer
from validators.validator import Validator
import atexit
from util import decode_auth_token
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
data_layer = None
validator = None


@app.before_first_request
def before_first_request_func():
    cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_THRESHOLD': 1000})
    cache.init_app(app)

    global data_layer
    if config('DB') == "mysql":
        data_layer = MySqlDBLayer(cache)
    else:
        data_layer = MongoDBLayer(cache)

    global validator
    validator = Validator()


@app.route("/horses")
def get_horses():
    pass


@app.route("/horse/<horse_id>")
def get_horse_by_id(horse_id):
    pass


@app.route("/race", methods=["POST"])
def start_race():
    try:
        content = request.json
        token = request.headers.get('auth-token')
        validator.validate_token(token, content['user_id'])
    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=401,
            mimetype='application/json'
        )
        return response

    race_id = data_layer.start_race(content['user_id'], content['horses'])
    resp = app.response_class(response=json.dumps({'race_id': race_id}),
                              status=200, mimetype='application/json')
    return resp


@app.route("/race/horse", methods=["PUT"])
def set_horse_finish_time():
    try:
        content = request.json
        token = request.headers.get('auth-token')
        user_id = decode_auth_token(token)

    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=401,
            mimetype='application/json'
        )
        return response
    data_layer.set_horse_finish_time(content["race_id"], content["horse_id"], content["finish_time"], user_id)
    resp = app.response_class(response=json.dumps({'race_id': content['race_id']}),
                              status=200, mimetype='application/json')
    return resp


@app.route("/race/<race_id>")
def get_race_by_id(race_id):
    try:
        content = request.json
        token = request.headers.get('auth-token')

    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=401,
            mimetype='application/json'
        )
        return response
    data_layer.get_race_by_id(race_id)


@app.route("/user", methods=["POST"])
def signup():
    content = request.json
    user_dict = data_layer.signup(content["name"], content["email"], content["password"])
    resp = app.response_class(response=json.dumps(user_dict),
                              status=200, mimetype='application/json')
    return resp


@app.route("/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "POST":  # The actual request following the preflight
        content = request.json
        user_dict = data_layer.login(content["email"], content["password"])
        resp = app.response_class(response=json.dumps(user_dict),
                                  status=200, mimetype='application/json')
        return resp


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@atexit.register
def goodbye():
    data_layer.shutdown()


if __name__ == "__main__":
    app.run()
