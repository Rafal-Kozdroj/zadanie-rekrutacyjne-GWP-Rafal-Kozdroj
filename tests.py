import unittest
import server

class TestStorage(unittest.TestCase):

    def test_put_key(self):
        values = {}
        key = "key"
        value = ("value", "text/plain")
        server.put_value(key, value, values)
        response = server.get_value(key, values)
        self.assertEqual(response, value)
