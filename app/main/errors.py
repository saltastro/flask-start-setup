from . import main


@main.errorhandler(500)
def internal_server_error(e):
    return 'Replace me with a proper error.'
