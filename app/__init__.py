from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify

from config import config, SSLStatus


bootstrap = Bootstrap()
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app, 'development')

    bootstrap.init_app(app)
    if not app.debug and not app.testing and app.config['SSL_STATUS'] == SSLStatus.ENABLED:
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

