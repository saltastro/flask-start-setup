import os
import subprocess

from bokeh.resources import CDN
from config import Config
from flask import Flask
from flask_assets import Environment
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from sqlalchemy.engine.url import make_url
from webassets.loaders import YAMLLoader

from config import config, SSLStatus


assets = Environment()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
migrate = Migrate()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app, config_name)

    app.config['ASSETS_DEBUG'] = app.config['DEBUG']

    assets.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    assets_config = os.path.join(os.path.dirname(__file__), os.pardir, 'webassets.yaml')
    assets._named_bundles = {}  # avoid duplicate registration in unit tests
    assets_loader = YAMLLoader(assets_config)
    bundles = assets_loader.load_bundles(assets)
    assets.register(bundles)

    if not app.debug and not app.testing and app.config['SSL_STATUS'] == SSLStatus.ENABLED:
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    @app.context_processor
    def bokeh_resources():
        return dict(bokeh_resources=CDN)

    @app.cli.command()
    def flyway():
        # parse the database URI
        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
        jdbc_url = 'jdbc:{drivername}://{host}:{port}/{database}'.format(drivername=url.drivername,
                                                                         host=url.host,
                                                                         port=url.port if url.port else 3306,
                                                                         database=url.database)
        username = url.username
        password = url.password

        # get Flyway command to run
        settings = Config.settings(os.environ['FLASK_CONFIG'])
        args = [settings['flyway_command'],
                '-url=' + jdbc_url,
                '-user=' + username,
                '-password=' + password,
                '-locations=filesystem:' + settings['migration_sql_dir'],
                'migrate']

        return subprocess.call(args)

    return app
