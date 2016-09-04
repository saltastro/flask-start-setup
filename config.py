import enum
import logging
import os

from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler


class SSLStatus(enum.Enum):
    ENABLED = True
    DISABLED = False


class Config:
    @staticmethod
    def settings(config_name):
        """Return the settings.

        Params:
        -------
        config_name: str
            Configuration name, as passed to the manage.py script.

        Returns:
        --------
        dict:
            The settings.
        """

        # set environment variables from file
        env_var_file = os.path.join(os.path.dirname(__file__), '.env')
        Config._set_environment_variables_from_file(env_var_file)

        prefix = Config.environment_variable_prefix()

        # initialise the setting variables

        # secret key
        secret_key = Config._environment_variable('SECRET_KEY', prefix=prefix, config_name=config_name)

        # database
        database_uri = Config._environment_variable('DATABASE_URI', prefix=prefix, config_name=config_name)

        # location of log file
        logging_file_base_path = Config._environment_variable('LOGGING_FILE_BASE_PATH',
                                                              prefix=prefix,
                                                              config_name=config_name)

        # logging level for logging to a file
        logging_file_logging_level = Config._logging_level(Config._environment_variable('LOGGING_FILE_LOGGING_LEVEL',
                                                                                        prefix=prefix,
                                                                                        config_name=config_name,
                                                                                        required=False,
                                                                                        default='ERROR'))

        # maximum size of a log file
        logging_file_max_bytes = Config._environment_variable('LOGGING_FILE_MAX_BYTES',
                                                              prefix=prefix,
                                                              config_name=config_name,
                                                              required=False,
                                                              default=5 * 1024 * 1024)

        # number of backed up log files kept
        logging_file_backup_count = Config._environment_variable('LOGGING_FILE_BACKUP_COUNT',
                                                                 prefix=prefix,
                                                                 config_name=config_name,
                                                                 required=False, default=10)

        # email addresses to send log messages to
        logging_mail_to_addresses = Config._environment_variable('LOGGING_MAIL_TO_ADDRESSES',
                                                                 prefix=prefix,
                                                                 config_name=config_name,
                                                                 required=False)
        if logging_mail_to_addresses:
            to_addresses = logging_mail_to_addresses.split(r'\s*,\s*')
        else:
            to_addresses = []

        # host for sending log emails
        logging_mail_host = Config._environment_variable('LOGGING_MAIL_HOST',
                                                         prefix=prefix,
                                                         config_name=config_name,
                                                         required=False)

        # logging level for logging to an email
        logging_mail_logging_level = Config._logging_level(Config._environment_variable('LOGGING_MAIL_LOGGING_LEVEL',
                                                                                        prefix=prefix,
                                                                                        config_name=config_name,
                                                                                        required=False,
                                                                                        default='ERROR'))

        # email address to use in the from field of a log email
        logging_mail_from_address = Config._environment_variable('LOGGING_MAIL_FROM_ADDRESS',
                                                                 prefix=prefix,
                                                                 config_name=config_name,
                                                                 required=False)

        # subject for log emails
        logging_mail_subject = Config._environment_variable('LOGGING_MAIL_SUBJECT',
                                                            prefix=prefix,
                                                            config_name=config_name,
                                                            required=False)

        # disable SSL?
        try:
            ssl_status = SSLStatus.ENABLED if int(os.environ.get(prefix + 'SSL_ENABLED')) != 0 else SSLStatus.DISABLED
        except:
            ssl_status = SSLStatus.ENABLED

        return dict(
            database_uri=database_uri,
            logging_file_base_path=logging_file_base_path,
            logging_file_logging_level=logging_file_logging_level,
            logging_file_max_bytes=logging_file_max_bytes,
            logging_file_backup_count=logging_file_backup_count,
            logging_mail_from_address=logging_mail_from_address,
            logging_mail_host=logging_mail_host,
            logging_mail_logging_level=logging_mail_logging_level,
            logging_mail_subject=logging_mail_subject,
            logging_mail_to_addresses=to_addresses,
            secret_key=secret_key,
            ssl_status=ssl_status
        )

    @staticmethod
    def _set_environment_variables_from_file(env_var_file):
        """Set environment variables from a file.

        If the given path exists, the corresponding file is read in. Each of its lines is parsed as KEY=VALUE, and the
        value VALUE is assigned to the environment variable KEY. Lines that cannot be parsed are ignored.

        Params:
        -------
        env_var_file: str
            Path of the file containing environment variable definitions. The file need not exist.
        """

        if not os.path.exists(env_var_file):
            return

        with open(env_var_file) as f:
            for line in f:
                parts = line.split('=')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    os.environ[key] = value


    @staticmethod
    def _environment_variable(raw_name, prefix, config_name, required=True, default=None):
        """Get the value of an environment variable.

        Params
        ------
        raw_name: str
            The "raw" name of the environment variable, from which the name for the given config_name can be
            constructed.
        prefix: str
            Prefix for all environment variables,, as given in root level file env_var_prefix.
        config_name: str
            Configuration name, as passed to the `manage.py` script.
        required: bool
            Whether the environment variable is required. A ValueErrort is raised if the variable is required and not
            set and None is passed as default value.
        default: str
            Value to return if the environment variable is not set.

        Returns
        -------
        str:
            Value of the environment variable names.
        """

        infix = dict(
            development='DEV_',
            testing='TEST_',
            production='',
        )
        if config_name not in infix:
            raise ValueError('Unknown configuration name: {0}'.format(config_name))
        name = prefix + infix[config_name] + raw_name

        variable_value = os.environ.get(key=name, default=default)
        if required and variable_value is None:
            raise ValueError('Environment variable not set: {0}'.format(name))

        return variable_value

    @staticmethod
    def environment_variable_prefix():
        """Get the prefix to use for the environment variables.

        Returns:
        --------
        str
            The prefix.
        """

        try:
            with open(os.path.join(os.path.dirname(__file__), 'env_var_prefix'), 'r') as f:
                return f.read().strip().rstrip('_') + '_'
        except:
            message = "The environment variable prefix couldn't be read in. " \
                      "This probably means that there is no root level file 'env_var_prefix'. This file must contain " \
                      "a single line with the prefix. Leading and trailing whitespace as well as leading underscores " \
                      "will be ignored."
            raise IOError(message)

    @staticmethod
    def _logging_level(name):
        """Return the logging level for a given name.

        Params:
        -------
        name: str
            Case-insensitive name of the logging level (such as 'ERROR' or 'WARNING').

        Returns:
        --------
        int
            The logging level.
        """

        # logging levels
        logging_levels = dict(
            CRITICAL=logging.CRITICAL,
            ERROR=logging.ERROR,
            WARNING=logging.WARNING,
            INFO=logging.INFO,
            DEBUG=logging.DEBUG,
            NOTSET=logging.NOTSET
        )

        name = name.upper()
        if name not in logging_levels:
            raise ValueError("Unknown logging level: {0}".format(name))
        return logging_levels[name]

    @staticmethod
    def init_app(app, config_name):
        """Initialises the Flask app.

        Params:
        -------
        app: Flask
            The Flask app.
        config_name: str
            The configuration name, as passed to the `manage.py` script.

        """
        settings = Config.settings(config_name)

        # secret key
        app.config['SECRET_KEY'] = settings['secret_key']

        # logging to file
        file_handler = RotatingFileHandler(filename=settings['logging_file_base_path'],
                                           maxBytes=settings['logging_file_max_bytes'],
                                           backupCount=settings['logging_file_backup_count'])
        file_handler.setLevel(settings['logging_file_logging_level'])
        app.logger.addHandler(file_handler)

        # logging to email
        if settings['logging_mail_host'] and settings['logging_mail_to_addresses']:
            smtp_handler = SMTPHandler(mailhost=settings['logging_mail_host'],
                                       fromaddr=settings['logging_mail_from_address'],
                                       toaddrs=settings['logging_mail_to_addresses'],
                                       subject=settings['logging_mail_subject'])
            smtp_handler.setLevel(settings['logging_mail_logging_level'])
            app.logger.addHandler(smtp_handler)

        # use SSL?
        app.config['SSL_STATUS'] = False  # settings['ssl_status']


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
