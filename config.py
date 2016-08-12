import logging
from logging.handlers import RotatingFileHandler


class Config:
    @staticmethod
    def init_app(app):
        file_handler = RotatingFileHandler(filename='/Users/christian/Desktop/LOGS/test.log', # os.environ.get('LOGFILE'),
                                           maxBytes=500,
                                           backupCount=10)
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
