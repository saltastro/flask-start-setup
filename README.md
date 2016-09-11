# Flask Start Setup

A simple framework for getting started with a Flask site using a MySQL database, which is based on the books *Flask Web Development* by Miguel Grinberg (O'Reilly) and *Mastering Flask* by Jack Stouffer (Packt Publishing).

## Installation

### On your machine for development

Download the content of the repository as a zip file and extract the file into a directory of your choice. Don't clone the repository, unless you are actually planning to update the start setup rather than to create a new Flask site.

You should then put the new directory (let's call it `/path/to/site`) under version control.

```bash
cd /path/to/site
git init
```

Make sure you've installed Python 3. Create a virtual environment

```bash
python3 -m venv venv
```

and then install the required Python libraries,

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Create a file `env_var_prefix` which contains a single line with the prefix to use for the environment variables (such as `FSS`). 

Define the required environment variables, as set out in the section *Environment variables* below. (If you are using an IDE, you might define these in your running configuration.)

You can then run the following commands for launching the (development) server or running the tests.

| Command | Purpose |
| --- | --- |
| `python manage.py runserver` | Launch the server |
| `./run_tests.sh` | Run the tests |

You might have to make the script `./run_tests.sh` executable,

```bash
chmod u+x run_tests.sh
```

Finally, you should modify the `README.md` file as required.

### On a remote server

**Important:** When the site is deployed, a file `.env` is created, which contains settings which must be kept secret. **Ensure that this file is not put under version control.**

Ubuntu 14.04 or higher must be running on the remote server, and standard commands like  The server should not be used for anything other than running the deployed website.

Create a user `deploy` for deploying the site, and give that user sudo permissions:

```bash
adduser deploy
gpasswd -a deploy sudo
```

You may choose another username for this user, but then you have to set the `<PREFIX>_SERVER_USERNAME` environment variable accordingly. See the section on environment variables for an explanation of the prefix.

Make sure wget is installed on the server.

Unless your repository has public access, you should also generate an SSL key for the deploy user. Check whether there is a file `~/.ssh/id_rsa.pub` already. If there isn't, create a new public key by running

```bash
ssh-keygen
```

If you don't choose the default file location, you'll have to modify the following instructions accordingly.

Once you have the key generated, find out whether the ssh agent is running.

```bash
ps -e | grep [s]sh-agent
```

If agent isn't running, start it with

```bash
ssh-agent /bin/bash
```

Load your new key into the ssh agent:

```bash
ssh-add ~/.ssh/id_rsa
```

You can now view your public key by means of

```bash
cat ~/.ssh/id_rsa.pub
```

Refer to to the instructions for your repository host like Github or Bitbucket as to how add your key top the host.

Once all the these prerequisites are in place you may deploy the site by running

```bash
fab setup
```

Supervisor, which is used for running the Nginx server, logs both the standard output and the standard error to log files in the folder `/var/log/supervisor`. You should check these log files if the server doesn't start.

For subsequent updates you may just run

```bash
fab deploy
```

If you get an internal server error after updating, there might still be a uWSGI process bound to the requested port. In this case rebooting the server should help.

## Environment variables

The configuration file makes use of various environment variables. All of these must have a common prefix which is defined in the root level file `env_var_prefix`. This file must have a single line with a text string, which is taken as the prefix. Leading and trailing white space as well as trailing underscores are ignored. An underscore is affixed to the prefix.

Most of the environment variables must be defined for various configurations, which are distinguished by different infixes for the variable name:

| Configuration name | Infix |
| --- | --- |
| development | `DEV_` |
| testing | `TEST_` |
| production | no prefix |

The script `run_tests.sh` uses the testing configuration. If you launch the server with the `manage.py` script, the development configuration is used. Code deployed to a remote server uses the production configuration.

For example, if the content of the file `env_var_prefix` is `MY_APP` an environment variable name for the development configuration could be `MY_APP_DEV_DATABASE_URI`.

The following variables are required for all modes:

| Environment variable | Description | Required | Default | Example |
| --- | --- | --- | --- | --- | --- |
| `DATABASE_URI` | URI for the database access | Yes | n/a | `mysql://user:password@your.server.ip/database` |
| `LOGGING_FILE_BASE_PATH` | Base path for the error log(s) | Yes | n/a | `/var/log/my-app/errors.log` |
| `LOGGING_FILE_LOGGING_LEVEL` | Level of logging for logging to a file | No | `ERROR` | `ERROR` |
| `LOGGING_FILE_MAX_BYTES` | Maximum number of bytes before which the log file is rolled over | No | 5242880 | 1048576 |
| `LOGGING_FILE_BACKUP_COUNT` | Number of backed up log files kept | No | 10 | 5 |
| `LOGGING_MAIL_FROM_ADDRESS` | Email address to use as from address in log emails | No | `no-reply@saaoo.ac.za` | `no-reply@saaoo.ac.za` |
| `LOGGING_MAIL_LOGGING_LEVEL` | Level of logging for logging to an email | No | `Error` | `ERROR` |
| `LOGGING_MAIL_SUBJECT` | Subject for the log emails | No | `Error Logged` | `Error on Website` |
| `LOGGING_MAIL_TO_ADDRESSES` | Comma separated list of email addresses to which error log emails are sent | No | None | `John  Doe <j.doe@wherever.org>, Mary Miller <mary@whatever.org>` |
| `SECRET_KEY` | Key for password seeding | Yes | n/a | `s89ywnke56` |
| `SSL_ENABLED` | Whether SSL should be disabled | No | 0 | 0 |

The following variable have no infix (but the prefix!) and are required only if you run the commands for setting up a remote server or deploying the site.

| Environment variable | Description | Required | Default | Example |
| --- | --- |
| DEPLOY_GIT_REPOSITORY | Git repository used for deploying the site | Yes | n/a | `git@bitbucket.org:your/repository.git` |
| DEPLOY_HOST | Address of the deployment server | Yes | n/a | `my-app.org.za` |
| DEPLOY_DOMAIN_NAME | Domain name for the website | No | Value of `DEPLOY_HOST` | `my-app.org.za` |
| DEPLOY_USERNAME | Username for the deployment server | No | `deploy` | `deploy` |
| DEPLOY_APP_DIR_NAME | Directory name for the deployed code | Yes | n/a | `my_app` |
| DEPLOY_WEB_USER | User for running the Tornado server | No | `www-data` | `www-data` |
| DEPLOY_WEB_USER_GROUP | Unix group of the user running the Tornado server | No | `www-data` | `www-data` |

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

## Error handling

The main blueprint includes some barebones error handlers in `app/main/errors.py`, which you have to customise. You might also want to add additional error handlers in this file, such as for file not found or authentication errors.

It is a good idea to log internal server errors and raised exceptions using logger described in the section on logging. The `errors.py` file does this in the `exception_raised` function.

## Authentication

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

## Templates

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

## Static files

Static files should be put in the directory `app/static` (which is Flask's default). Static files have two problems:

1. They should be bundled together, to avoid unnecessarily many HTTP requests.
2. More importantly, they are cached by browsers, and you must ensure that an updated version will actually be loaded by the browser.

This framework addresses both issues by using the Flask-Assets library, which creates bundles and attaches a GET parameter based on the bundles hash. To make use of this, you first have to define your bundles in the root-level file `webassets.yaml`. Here is an example:

```yaml
js-all:
    filters: rjsmin
    output: cache/all.js
    contents:
        - js/a.js
        - js/b.js
        - js/c/d.js

css-all:
    filters: yui_css
    output: cache/all.css
    contents:
        - css/main/a.css
        - css/main/b.css
```

Note the dashes before the file paths - these are indeed required!

Then you can include any of the defined bundles in a Jinja2 template by using the `assets` tag. For example,

```
{% block scripts %}
{{ super() }}
{% assets 'js-all' %}
<script src="{{ ASSET_URL }}"></script>
{% endassets %}
{% endblock %}
```

The generated bundles are put in the directory `app/static/cache`. When running the server in test or development mode, the original, individual files rather than the bundles will be included.

The deploy script automatically generates the bundles on the production server, rather than relying on them being created on the fly when a page is requested. This implies that you *don't* have to give the web user write access to the cache directory.

## Database access

The framework includes Flask-SQLAlchemy and makes an SQLAlchemy instance available as a variable `db` in the `app` package. You can, for example, use this to create a Pandas dataframe from an SQL query:

```python
# Pandas doesn't ship with this framework, but you can install it with
# pip install pandas
import pandas as pd

from app import db

sql = 'SELECT * FROM SomeTable'
df = pd.read_sql(sql, db.engine)
```

The framework installs mysqlclient. If you aren't using MySQL, you may uninstall this library, and you have to install whatever library you require.

Note that the framework doesn't create any ORM models or offers any database migration support.

## Testing

Unit tests, Behave tests and PEP8 tests are supported.

### Unit tests

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

### Behave tests

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

### PEP8 tests

The testing script mentioned in the next subsection includes PEP8 checking.

### Running the tests 

The Bash script `run_tests.sh` allows you to run your tests. In addition it uses the `pycodestyle` module to check compliance with PEP8. Regarding the latter a maximum line length of 120 is assumed and module level imports aren't forced to be at the top of a file.

If you want to enforce that git commits can only be pushed if all tests are passed, you may use a git hook. If there is a pre-push hook already, modify it to include the content of the `run_tests.sh` script. Otherwise just copy the script and ensure the hook is executable:

```bash
cp run_tests.sh .git/hooks/pre-push
chmod u+x .git/hooks/pre-push
```

## Errors

Errors are handled by the module `app.main.errors`, which makes use of Jinja2 templates. You might want to to customise these templates.



