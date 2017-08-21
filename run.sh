#!/bin/sh
. venv/bin/activate
export FLASK_APP="server.py"
exec flask run -h 127.0.0.1 -p 8080 "$@"
