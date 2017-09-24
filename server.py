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

def create_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(error):
    """Close the database connection"""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

def is_key_in_db(key, db):
    cur = db.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM ENTRIES WHERE ID=?)", (key,))
    exists = cur.fetchone()
    if exists is 0:
        return False
    return True

def put_value(key, value, mime, db):
    exists = is_key_in_db(key, db)
    cur = db.cursor()
    cur.execute("INSERT OR REPLACE INTO ENTRIES VALUES (?, ?, ?)",
                (key, value, mime))
    db.commit()
    return not exists

def get_value(key, db):
    cur = db.cursor()
    cur.execute("SELECT DATA, MIME FROM ENTRIES WHERE ID=?", (key,))
    return cur.fetchone()

def remove_value(key, db):
    exists = is_key_in_db(key, db)
    if exists is False:
        return False
    cur = db.cursor()
    cur.execute("DELETE FROM ENTRIES WHERE ID = ?", key)
    db.commit()
    return True

def get_keys(db):
    cur = db.execute("SELECT ID FROM ENTRIES ORDER BY ID DESC")
    keys = cur.fetchall()
    return keys

def validate_key(key):
    if not key.isalnum():
        return 400
    if len(key) > KEY_MAX_LEN:
        return 400

def validate_data(data):
    if len(data) > VALUE_MAX_SIZE:
            return 413

@app.route("/api/objects", methods=["GET"])
def show_keys():
    """Return list of keys of all stored values."""
    db = get_db()
    keys = get_keys(db)
    response = make_response(keys)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/api/objects/<key>", methods=["GET"])
def handle_get(key):
    print(request.method)
    return_code = validate_key(key)
    if return_code is not None:
        return "", return_code
    value = get_value(key, get_db())
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
    mime = request.headers["Content-Type"]
    if put_value(key, data, mime, get_db()):
        return "", 201
    return "", 200

@app.route("/api/objects/<key>", methods=["DELETE"])
def handle_delete(key):
    print(request.method)
    return_code = validate_key(key)
    if return_code is not None:
        return "", return_code
    if remove_value(key, get_db()):
        return "", 200
    return "", 404
