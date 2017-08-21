#!/usr/bin/env python3
from flask import Flask
from flask import request
import re
app = Flask(__name__)

values = {}

VALUE_MAX_SIZE = 1024 * 1024 * 1024
KEY_PATTERN = re.compile("[a-zA-z0-9]+")

def put_value(key, value):
    created = False
    if key not in values:
        created = True
    values[key] = value
    return created

@app.route("/api/objects/<key>", methods=["GET", "PUT", "DELETE"])
def objects(key):
    if request.method == "PUT":
        if not KEY_PATTERN.match(key):
            return "Bad Request", 400
        value = request.data
        if len(value) > VALUE_MAX_SIZE:
            return "Request Entity Too Large", 413
        if put_value(key, value):
            return "Created", 201
        return "Ok", 200
    return "Not implemented yet", 404
