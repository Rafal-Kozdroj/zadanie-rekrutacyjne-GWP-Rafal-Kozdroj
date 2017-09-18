import json
from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

VALUE_MAX_SIZE = 1024 * 1024
KEY_MAX_LEN = 100

FILENAME = "values.txt"

def put_value(key, value, values):
    created = False
    if key not in values:
        created = True
    values[key] = value
    save_to_file(values, FILENAME)
    return created

def get_value(key, values):
    if key in values:
        return values[key]
    return None

def remove_value(key, values):
    removed = False
    if key in values:
        del values[key]
        save_to_file(values, FILENAME)
        removed = True
    return removed

def save_to_file(values, filename):
    file = open(filename, "w")
    file.write(json.dumps(values))
    file.close()

def load_file(filename):
    file = open(filename, "r")
    json_data = json.load(file)
    file.close()
    return json_data

values = load_file(FILENAME)

@app.route("/api/objects", methods=["GET"])
def send_keys():
    keys = list(values.keys())
    json_data = json.dumps(keys)
    response = make_response(json_data)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/api/objects/<key>", methods=["GET", "PUT", "DELETE"])
def objects(key):
    print(request.method)
    if not key.isalnum():
        return "", 400
    if len(key) > KEY_MAX_LEN:
        return "", 400
    if request.method == "PUT":
        data = request.get_data()
        if len(data) > VALUE_MAX_SIZE:
            return "", 413
        if "Content-Type" not in request.headers:
            return "", 400
        value = (data.decode(), request.headers["Content-Type"])
        if put_value(key, value, values):
            return "", 201
        return "", 200
    elif request.method == "GET":
        value = get_value(key, values)
        if value is None:
            return "", 404
        response = make_response(value[0])
        response.headers["Content-Type"] = value[1]
        return response
    elif request.method == "DELETE":
        if remove_value(key, values):
            return "", 200
        return "", 404
