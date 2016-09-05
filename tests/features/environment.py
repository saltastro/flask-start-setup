from app import create_app


def before_scenario(context, scenario):
    """Set up the Flask environment.

    The Flask app and its context are created, and stored in the context variable. In addition a test client using
    cookies is created and stored in the context variable.

    Params:
    -------
    context: object
        Behave context.
    scenario: object
        Behave scenario.

    """
    context.app = create_app('testing')
    context.app_context = context.app.app_context()
    context.app_context.push()
    context.client = context.app.test_client(use_cookies=True)


def after_scenario(context, scenario):
    """Tear down the Flask environment.

    Params:
    -------
    context: object
        Behave context.
    scenario: object
        Behave scenario.
    """

    context.app_context.pop()
