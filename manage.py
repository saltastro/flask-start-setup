#!/usr/bin/env python
import os

from app import create_app
from flask_script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'development')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def test():
    raise NotImplementedError('Please use the command "./run_tests.sh" for running the tests.')


@manager.command
def deploy():
    raise NotImplementedError('Please use the command "fab setup" for setting up the server and the command '
                              '"fab deploy" for deploying code afterwards.')

if __name__ == '__main__':
    manager.run()