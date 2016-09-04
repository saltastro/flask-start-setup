from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sslify import SSLify

from config import config, SSLStatus


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app, config_name)

    login_manager.init_app(app)
    bootstrap.init_app(app)

    if not app.debug and not app.testing and app.config['SSL_STATUS'] == SSLStatus.ENABLED:
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
