from flask import current_app

from . import main


@main.errorhandler(500)
def internal_server_error(e):
    return 'Replace me with proper error handling.'


@main.errorhandler(404)
def file_not_found_error(e):
    return 'Replace me with proper error handling.'


@main.errorhandler(Exception)
def exception_raised(e):
    current_app.logger.error(str(e))
    return 'Replace me with proper error handling.'
