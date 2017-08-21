#!/usr/bin/env python3
import http.server
import socketserver
import re

PORT = 8080
MAX_VALUE_SIZE = 1024 * 1024 * 1024

values = {}

key_pattern = re.compile("[a-zA-z0-9]+")

class handler(http.server.BaseHTTPRequestHandler):
    def do_PUT(self):
        print("path: " + self.path)
        if not self.path.startswith("/api/objects/"):
            self.send_error(400)
            self.end_headers()
            return
        key = self.path[13:]
        print("key: " + key)
        value = self.rfile.read()
        print("value: " + str(value))
        response = 200
        if key not in values:
            response = 201
        values[key] = value
        self.send_response(response)
        self.end_headers()
        return

Handler = handler

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
