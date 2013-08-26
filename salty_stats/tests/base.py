import unittest

from salty_stats import db


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.Session = db.create_session_class()

    def setUp(self):
        self.session = self.Session()
