import os

from flask import Flask
from flask_assets import Environment
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from webassets.loaders import YAMLLoader

from config import config, SSLStatus


assets = Environment()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app, config_name)

    assets.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    assets_config = os.path.join(os.path.dirname(__file__), os.pardir, 'webassets.yaml')
    assets_loader = YAMLLoader(assets_config)
    bundles = assets_loader.load_bundles(assets)
    assets.register(bundles)

    if not app.debug and not app.testing and app.config['SSL_STATUS'] == SSLStatus.ENABLED:
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
