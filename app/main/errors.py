from flask import current_app, render_template

from . import main


@main.errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(str(e))
    return render_template('500.html'), 500


@main.errorhandler(404)
def file_not_found_error(e):
    return render_template('404.html'), 404


@main.errorhandler(Exception)
def exception_raised(e):
    current_app.logger.error(str(e))
    return render_template('500.html'), 500
