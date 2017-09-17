#!/usr/bin/env python3
import unittest
from flask import Flask
import server

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        server.app.testing = True
        self.app = server.app.test_client()

    def test_put_key(self):
        values = {}
        key = "key"
        value = ("value", "text/plain")
        server.put_value(key, value, values)
        response = server.get_value(key, values)
        self.assertEqual(response, value)

if __name__ == "__main__":
    unittest.main()
