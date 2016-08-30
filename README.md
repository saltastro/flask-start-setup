# Flask Start Setup

A simple framework for getting started with a Flask site which is based on the book *Flask Web Development* by Miguel Grinberg (O'Reilly).

## Installation

### On your machine for development

Download the content of the repository as a zip file and extract the file into a directory of your choice. Don't clone the repository, unless you are actually planning to update the start setup rather than to create a new Flask site.

You should then put the new directory (let's call it `/path/to/site`) under version control.

```bash
cd /path/to/site
git init
```

Make sure you've installed Python 3. If you want to use a virtual environment, you can create one with

```bash
python3 -m venv venv
```

and then install the required Python libraries,

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Define the required environment variables, as set out in the section *Environment variables* below. (If you are using an IDE, you might define these in your running configuration.)

You can then run the following commands for launching the (development) server or running the tests.

| Command | Purpose |
| --- | --- |
| `python manage.py runserver` | Launch the server |
| `python manage.py test` | Run the tests |

### On a remote server

TBD

## Environment variables

The configuration file makes use of various environment variables. All of these must have a common prefix which is defined in the root level file `env_var_prefix`. This file must have a single line with a text string, which is taken as the prefix. Leading and trailing white space as well as trailing underscores are ignored. An underscore is affixed to the prefix.

Most of the environment variables must be defined for various configurations, which are distinguished by different infixes for the variable name:

| Configuration name | Infix |
| -- | -- |
| development | `DEV_` |
| testing | `TEST_` |
| production | no prefix |

Here tests refer to (automated) tests on your machine, and the deployment server could be the production server, or a server for testing.

For example, if the content of the file `env_var_prefix` is `MY_APP` an environment variable name for the development configuration could be `MY_APP_DEV_DATABASE_URI`.

The following variables are required for all modes:

| Environment variable | Description | Required | Default | Example |
| -- | -- | -- | -- | -- | -- |
| `DATABASE_URI` | URI for the database access | Yes | n/a | `mysql://user:password@your.server.ip/database` |
| `LOGGING_FILE_BASE_PATH` | Base path for the error log(s) | Yes | n/a | `/var/log/my-app/errors.log` |
| `LOGGING_FILE_LOGGING_LEVEL` | Level of logging for logging to a file | No | `ERROR` | `ERROR` |
| `LOGGING_FILE_MAX_BYTES` | Maximum number of bytes before which the log file is rolled over | No | 5242880 | 1048576 |
| `LOGGING_FILE_BACKUP_COUNT` | Number of backed up log files kept | No | 10 | 5 |
| `LOGGING_MAIL_FROM_ADDRESS` | Email address to use as from address in log emails | No | `no-reply@saaoo.ac.za` | `no-reply@saaoo.ac.za` |
| `LOGGING_MAIL_LOG_LEVEL` | Level of logging for logging to an email | No | `Error` | `ERROR` |
| `LOGGING_MAIL_SUBJECT` | Subject for the log emails | No | `Error Logged` | `Error on Website` |
| `LOGGING_MAIL_TO_ADDRESSES` | Comma separated list of email addresses to which error log emails are sent | No | None | `John  Doe <j.doe@wherever.org>, Mary Miller <mary@whatever.org>` |
| `SECRET_KEY` | Key for password seeding | Yes | n/a | `s89ywnke56` |
| `SSL_ENABLED` | Whether SSL should be disabled | No | 0 | 0 |

The following variable needs to be defined for production only.

| Environment variable | Description | Example |
| -- | -- |
| SERVER_ADDRESS | Address of the deployment server | `www.my-app.org.za` |
| SERVER_USERNAME | Username for the deployment server | `deployment_user` |

## Adding your own environment variables

If you want to add your own environment variables for the various configuration names, you should modify the `_settings` method in `config.py`. You can get the value of your variable with the `_environment_variable` method, and you have to include this in the returned dictionary.

For example, assume you want to use an LDAP server for authentication and want to set this in an environment variable `LDAP_SERVER` (with the different prefixes for the various configurations). Then you could modify the `_settings` method as follows.

```python
def _settings(config_name)
    ...
    # LDAP server for user authentication
    ldap_server = Config._environment_variable('LDAP_SERVER', config_name)
    ...
    return dict(
        ...
        ldap_server=ldap_server,
        ...
    )
```

You can then access the variable value as `settings['ldap_server']` in the `init_app` method of `config.py`.

## Logging

The app logs errors etc. to file and optionally can send an email whenever a message is logged. Different logging levels can be set for both by means of the respective environment variables. The available levels are those defined in the `logging` module, i.e. `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` and `NOTSET`.

The log files are automatically rolled over when their size reaches the value specified by the environment variable  `LOGGING_FILE_MAX_BYTES`. The number of backed up copies kept is set by the environment variable `LOGGING_FILE_BACKUP_COUNT`. If `LOGGING_FILE_MAX_BYTES` or `LOGGING_FILE_BACKUP_COUNT` is 0, the log file is never rolled over. See the documentation for `logging.handlers.RotatingFileHandler` for more details.

The logging handler are attached to the app. So in order to access them, you have to use code like the following.

```python
from flask import current_app

current_app.logger.error('This is an error.')
current_app.logger.warning('This is a warning.')
```

# Error handling

The main blueprint includes some barebones error handlers in `app/main/errors.py`, which you have to customise. You might also want to add additional error handlers in this file, such as for file not found or authentication errors.

It is a good idea to log internal server errors and raised exceptions using logger described in the section on logging. The `errors.py` file does this in the `exception_raised` function.

# Authentication

Authentication with Flask-Login is included. If you don't need this, you should remove the folder `app/auth`, remove the login manager initialisation

```python
from flask.ext.login import LoginManager
...
login_manager = LoginManager()
...
def create_app(config_name):
    ...
    login_manager.init_app(app)
    ...
```

from the app's initialisation file `app/_init__.py`, remove the folder `app/templates/auth` and remove the Flask-Login dependency

```
Flask-Login==x.y.z
```

from the file `requirements.txt` in the root folder. (`x.y.z` denotes a version number.)

The file `app/auth/views.py` contains an example implementation of a user class, as well as the functions required for the login manager. While you have to replace these with whatever need in your project, they should give you an idea of how to work with the login manager. More details can be found in Chapter 8 of Miguel Grinberg's book *Flask Web Development* (O'Reilly).

# Templates

The `templates` folder contains a base template (`base.html`), a home page (`index.html`) and an authentication form (`auth/login.html`). All of these should be customised to suit your needs.

While all of the templates use Flask-Bootstrap, there is of course no need for that. If you don't want to use Bootstrap, you should remove the line

```html
{% extends "bootstrap/base.html" %}
```

from `base.html`, the line

```html
{% import "bootstrap/wtf.html" as wtf %}
```

from `auth/login.html` (and update the rest of that template accordingly), the Bootstrap initialisation

```python
from flask_bootstrap import Bootstrap
...
bootstrap = Bootstrap()
...
def create_app(config_name):
    ...
    bootstrap.init_app(app)
    ...
```

from the app's init file (`app/__init__.py`), and the Flask-Bootstrap dependency

```
Flask-Bootstrap==w.x.y.z
```

from the file `requirements.txt` in the root folder. (`w.x.y.z` denotes a version number.)

## Testing

You should add all your unit tests to the folder `tests/unittests`. BDD feature files should be put in the folder `tests/features`, and the corresponding step implementation files in `tests/features/steps`. Examples are included both for unit tests and for BDD tests.

The Bash script `run_tests.sh` allows you to run your tests. In addition it uses the `pycodestyle` module to check compliance with PEP8. Regarding the latter a maximum line length of 120 is assumed and module level imports aren't forced to be at the top of a file.

If you want to enforce that git commits can only be pushed if all tests are passed, you may use a git hook. If there is a pre-push hook already, modify it to include the content of the `run_tests.sh` script. Otherwise just copy the script ands ensure the hook is executable:

```bash
cp run_tests.sh .git/hooks/pre-push
chmod u+x .git/hooks/pre-push
```




