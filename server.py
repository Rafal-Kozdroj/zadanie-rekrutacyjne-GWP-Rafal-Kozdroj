"""Simple key-value storage server"""
import os
import json
import sqlite3
from flask import Flask, request, make_response, g

# Create application instance
app = Flask(__name__)

# Load configuration
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'server.db')
))
app.config.from_envvar('SERVER_SETTINGS', silent=True)

VALUE_MAX_SIZE = 1024 * 1024
KEY_MAX_LEN = 100

FILENAME = "values.txt"

def connect_db():
    """Connect to the database"""
    rv = sqlite3.connect(app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Get the database connection"""
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Close the database connection"""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

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

def validate_key(key):
    if not key.isalnum():
        return 400
    if len(key) > KEY_MAX_LEN:
        return 400

def validate_data(data):
    if len(data) > VALUE_MAX_SIZE:
            return 413

@app.route("/api/objects", methods=["GET"])
def send_keys():
    keys = list(values.keys())
    json_data = json.dumps(keys)
    response = make_response(json_data)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/api/objects/<key>", methods=["GET"])
def handle_get(key):
    print(request.method)
    return_code = validate_key(key)
    if return_code is not None:
        return "", return_code
    value = get_value(key, values)
    if value is None:
        return "", 404
    response = make_response(value[0])
    response.headers["Content-Type"] = value[1]
    return response

@app.route("/api/objects/<key>", methods=["PUT"])
def handle_put(key):
    print(request.method)
    return_code = validate_key(key)
    if return_code is not None:
        return "", return_code
    data = request.get_data()
    return_code = validate_data(data)
    if return_code is not None:
        return "", return_code
    if "Content-Type" not in request.headers:
        return "", 400
    value = (data.decode(), request.headers["Content-Type"])
    if put_value(key, value, values):
        return "", 201
    return "", 200

@app.route("/api/objects/<key>", methods=["DELETE"])
def handle_delete(key):
    print(request.method)
    return_code = validate_key(key)
    if return_code is not None:
        return "", return_code
    if remove_value(key, values):
        return "", 200
    return "", 404
