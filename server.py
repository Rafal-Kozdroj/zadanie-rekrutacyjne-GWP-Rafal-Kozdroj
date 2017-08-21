#!/usr/bin/env python3
import http.server
import re
import json

PORT = 8080
SERVER_ADDRESS = ("127.0.0.1", PORT)
MAX_VALUE_SIZE = 1024 * 1024 * 1024

values = {}

key_pattern = re.compile("[a-zA-z0-9]+")

class handler(http.server.BaseHTTPRequestHandler):
    def do_PUT(self):
        print("path: " + self.path)
        if not self.path.startswith("/api/objects/"):
            self.send_error(404)
            self.end_headers()
            return
        key = self.path[13:]
        print("key: " + key)
        if not key_pattern.match(key):
            self.send_error(400)
            self.end_headers()
        value = self.rfile.read()
        print("value: " + str(value))
        response = 200
        if key not in values:
            response = 201
        values[key] = value
        self.send_response(response)
        self.end_headers()

    def do_GET(self):
        print("path: " + self.path)
        if self.path == "/api/objects":
            # return keys
            keys = list(values.keys())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(keys).encode())
            self.wfile.write("\n".encode())
            return
        self.send_response(200)
        self.end_headers()

Handler = handler

httpd = http.server.HTTPServer(SERVER_ADDRESS, Handler)
httpd.serve_forever()
