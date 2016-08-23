from . import main


@main.route('/')
def hello_world():
    return '<h1>Hello</h1>'