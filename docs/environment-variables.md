# Environment variables

The configuration file makes use of various environment variables. All of these must have a common prefix which is defined in the root level file `env_var_prefix`. This file must have a single line with a text string, which is taken as the prefix. Leading and trailing white space as well as trailing underscores are ignored. An underscore is affixed to the prefix.

Most of the environment variables must be defined for various configurations, which are distinguished by different infixes for the variable name:

| Configuration name | Infix |
| --- | --- |
| development | `DEV_` |
| testing | `TEST_` |
| production | no prefix |

The script `run_tests.sh` uses the testing configuration. Code deployed to a remote server uses the production configuration. Otherwise the configuration specified by the `FLASK_APP_CONFIG` environment variable.

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

The following variable have no infix (but the prefix!) and are required only if you run the commands for setting up a remote server or deploying the site, or if you perform a database migration.

| Environment variable | Description | Required | Default | Example |
| --- | --- |
| DEPLOY_GIT_REPOSITORY | Git repository used for deploying the site | Yes | n/a | `git@bitbucket.org:your/repository.git` |
| DEPLOY_HOST | Address of the deployment server | Yes | n/a | `my-app.org.za` |
| DEPLOY_DOMAIN_NAME | Domain name for the website | No | Value of `DEPLOY_HOST` | `my-app.org.za` |
| DEPLOY_USER | User for the deployment server | No | `deploy` | `deploy` |
| DEPLOY_USER_GROUP | Unix group for the deploy user | No | Value of `DEPLOY_USER` | `deploy` |
| DEPLOY_APP_DIR_NAME | Directory name for the deployed code | Yes | n/a | `my_app` |
| DEPLOY_WEB_USER | User for running the Tornado server | No | `www-data` | `www-data` |
| DEPLOY_WEB_USER_GROUP | Unix group of the user running the Tornado server | No | `www-data` | `www-data` |
| DEPLOY_BOKEH_SERVER_PORT | No | 5100 | 5100 |
| DB_MIGRATION_TOOL | Tool to use for database migration | No | `None` | `Flask-Migrate` |
| DB_MIGRATION_SQL_DIR | Directory containing the migration SQL scripts | no | `db_migrations` | `db_migrations` |
| DB_MIGRATION_FLYWAY_COMMAND | Command for running flyway | No | `flyway` | `/path/to/flyway` |

You can disable logging as well:

| Environment variable | Description | Required | Default | Example |
| --- | --- |
| WITH_LOGGING | Whether to log errors (1) or not (0) | No | 1 | 1 |

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
