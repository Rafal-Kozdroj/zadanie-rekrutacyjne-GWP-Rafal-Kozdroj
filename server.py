#!/usr/bin/env python3
import json
from flask import Flask
from flask import Response
from flask import request

app = Flask(__name__)

values = {}

VALUE_MAX_SIZE = 1024 * 1024 * 1024
KEY_MAX_LEN = 100

def put_value(key, value, values):
    created = False
    if key not in values:
        created = True
    values[key] = value
    return created

def get_value(key, values):
    if key in values:
        return values[key]
    return None

def remove_value(key, values):
    removed = False
    if key in values:
        del values[key]
        removed = True
    return removed

@app.route("/api/objects", methods=["GET"])
def send_keys():
    keys = list(values.keys())
    return json.dumps(keys)

@app.route("/api/objects/<key>", methods=["GET", "PUT", "DELETE"])
def objects(key):
    if not key.isalnum():
        return "", 400
    if len(key) > KEY_MAX_LEN:
        return "", 400
    if request.method == "PUT":
        value = request.get_data()
        if len(value) > VALUE_MAX_SIZE:
            return "", 413
        if put_value(key, value, values):
            return "", 201
        return "", 200
    elif request.method == "GET":
        value = get_value(key, values)
        if value is None:
            return "", 404
        return value, 200
    elif request.method == "DELETE":
        if remove_value(key, values):
            return "", 200
        return "", 404
    return "", 400
