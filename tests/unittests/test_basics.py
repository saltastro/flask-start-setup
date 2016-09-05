from flask import current_app

from tests.unittests.base import BaseTestCase


class BasicsTestCase(BaseTestCase):
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_homepage_exists(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
