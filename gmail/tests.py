

import unittest
import base64
import gmail

class TestGmail(unittest.TestCase):
    
    def setUp(self):
        self.username = 'charlie@joymetrics.com'
        self.password = 'c2FsbW9uM2xsYQ=='

        self.invalid_imap_host = ""
        self.invalid_username = 'xxx@xxx'

    def test_connect(self):
        gmail = Gmail(self.username)
        connection = gmail.connect()

        self.assertIsNotNone(connection)

    def test_login(self):
        gmail = Gmail(self.username)
        connection = gmail.connect()

        logged_in = gmail.login(base64.b64decode(self.password))
        self.assertTrue(logged_in)

    def test_login_error(self):
        gmail = Gmail(self.username)
        connection = gmail.connect()

        with self.assertRaises(Exception):
            gmail.login('')





if __name__ == "__main__":
    unittest.main()

