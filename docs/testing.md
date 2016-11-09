# Testing

Unit tests, Behave tests and PEP8 tests are supported.

## Unit tests

You should add all your unit tests to the folder `tests/unittests`. For convenience a base test case class `tests.unittests.base.BaseTestCase` is provided, which sets up and tears down the Flask environment. This class also creates a test client, which can be accessed as `self.client`. This test client is using cookies.

In addition, the `test.unittests.base` module offers a class `NoAuthBaseTestCase`, which extends the `BaseTestCase` class and disables authentication, meaning that `login_required` decorators for routes are ignored.

A unit test using the `NoAuthBaseTestClass` might look as follows.

```python
from tests.unittests.base import NoAuthBaseTestCase


class NoAuthBasicsTestCase(NoAuthBaseTestCase):
    def test_homepage_exists(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
```

## Behave tests

[Behave](https://pythonhosted.org/behave/index.html) feature files should be put in the folder `tests/features`, and the corresponding step implementation files in `tests/features/steps`.

The context variable passed to the step implementations provides access to the Flask app and a test client (which are set up in the `environment.py` module). The test client is using cookies. The following example illustrates how the test client can  be used.

```python
from behave import *

use_step_matcher("re")


@when('I access the homepage')
def step_impl(context):
    context.response = context.client.get('/')


@then('I get a page with no error')
def step_impl(context):
    assert context.response.status_code == 200
```

## PEP8 tests

The testing script mentioned in the next subsection includes PEP8 checking.

## Running the tests 

The Bash script `run_tests.sh` allows you to run your tests. In addition it uses the `pycodestyle` module to check compliance with PEP8. Regarding the latter a maximum line length of 120 is assumed and module level imports aren't forced to be at the top of a file.

If you want to enforce that git commits can only be pushed if all tests are passed, you may use a git hook. If there is a pre-push hook already, modify it to include the content of the `run_tests.sh` script. Otherwise just copy the script and ensure the hook is executable:

```bash
cp run_tests.sh .git/hooks/pre-push
chmod u+x .git/hooks/pre-push
```
