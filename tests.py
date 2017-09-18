#!/usr/bin/env python3
import unittest
from flask import Flask
import server

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        server.app.testing = True
        self.app = server.app.test_client()

    def test_valid_key(self):
        key = "key"
        value = b"value"
        # test putting new key
        response = self.app.put("api/objects/{}".format(key), data=value)
        self.assertEqual(response.status_code, 201)
        #test getting existing key
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, value)
        # test putting existing key
        response = self.app.put("api/objects/{}".format(key), data=value)
        self.assertEqual(response.status_code, 200)
        #test getting existing key
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, value)
        # test removing existing key
        response = self.app.delete("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 200)
        # test removing non-existing key
        response = self.app.delete("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 404)

    def test_invalid_key(self):
        key = "key--"
        value = b"value"
        # test putting key
        self.app.put("api/objects/{}".format(key), data=value)
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)
        # test getting key
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)
        # test deleting key
        response = self.app.delete("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)

    def test_too_big_key(self):
        key = "0" * (server.KEY_MAX_LEN + 1)
        value = b"value"
        # test putting key
        self.app.put("api/objects/{}".format(key), data=value)
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)
        # test getting key
        response = self.app.get("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)
        # test deleting key
        response = self.app.delete("api/objects/{}".format(key))
        self.assertEqual(response.status_code, 400)

    def test_too_big_data(self):
        key = "key"
        value = b"0" * (server.VALUE_MAX_SIZE + 1)
        # test putting key
        response = self.app.put("api/objects/{}".format(key), data=value)
        self.assertEqual(response.status_code, 413)

    def test_get_keys(self):
        response = self.app.get("api/objects")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
