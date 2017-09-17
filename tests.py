#!/usr/bin/env python3
import unittest
from flask import Flask
import server

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        server.app.testing = True
        self.app = server.app.test_client()

    def test_put_key(self):
        key = "key"
        value = b"value"
        self.app.put("api/objects/{}".format(key), data=value)
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, value)

if __name__ == "__main__":
    unittest.main()
