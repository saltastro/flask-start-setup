# Database

The framework includes Flask-SQLAlchemy and makes an SQLAlchemy instance available as a variable `db` in the `app` package. 

## Database access

You can, for example, access the database by creating a Pandas dataframe from an SQL query:

```python
# Pandas doesn't ship with this framework, but you can install it with
# pip install pandas
import pandas as pd

from app import db

sql = 'SELECT * FROM SomeTable'
df = pd.read_sql(sql, db.engine)
```

The framework installs mysqlclient. If you aren't using MySQL, you may uninstall this library, and you have to install whatever library you require.

Note that the framework doesn't create any ORM models.

## Database migrations

You must set the `DB_MIGRATION_TOOL` environment variable to choose which tool (if any) to use for performing a database migration when deploying your code. The options are:

| Database migration option | Variable value |
| Use Flask-Migrate | Flask-Migrate |
| Use Flyway | Flyway |
| Don't migrate the database | None |

### Using Flask-Migrate

See [https://flask-migrate.readthedocs.io/en/latest/](https://flask-migrate.readthedocs.io/en/latest/) for an introduction to using Flask-Migrate. When you call it with its Flask command,

```bash
flask db ...
```

it will access the same database used when you run `flask run` (i.e. the one for the configuration set by the environment variable `FLASK_CONFIG`). Use the environment variable `DB_MIGRATION_SQL_DIR` for setting the folder containing your migration scripts.

You can choose the directory for the migration script with the `-d` flag. For example, if you want to use the directory provided by this framework, you would initialise the migration by means ofd running

```bash
flask db init -d db_migrations
```

Similarly, you would create the migration scripts by running

```bash
flask db migrate -m 'some descriptive message' -d db_migrations
```

And finally, you would push the migration changes to the database by running

```bash
flask db upgrade -d db_migrations
``` 

### Using Flyway

For convenience, there is a Flask command for running Flyway:

```bash
flask flyway
```

This will migrate the same database used when you run `flask run` (i.e. the one for the configuration set by the environment variable `FLASK_CONFIG`). Use the environment variables `DB_MIGRATION_FLYWAY_COMMAND` and `DB_MIGRATION_SQL_DIR` for setting the Flyway command (if just using `flyway` doesn't work) and the folder containing your migration scripts.
