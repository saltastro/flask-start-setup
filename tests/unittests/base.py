import unittest

from app import create_app


class BaseTestCase(unittest.TestCase):
    """Base class for Flask unit tests.

    The class ensures that the Flask app and its context are created before the first unit test, and thatv the context
    is removed again after the last test.

    It also creates a test client as `self.client`. This test client uses cookies.
    """

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()


class NoAuthBaseTestCase(BaseTestCase):
    """Base class for Flask unit tests without authentication.

    Apart from the functionality provided by the BaseTestClass, this class disables authentication checking, so that
    login_required decorators will be ignored.
    """

    def setUp(self):
        BaseTestCase.setUp(self)
        self.app.config['LOGIN_DISABLED'] = True
        self.app.login_manager.init_app(self.app)
