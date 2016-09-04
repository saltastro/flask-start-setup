from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import create_app

app = WSGIContainer(create_app('production'))

http_server = HTTPServer(app)
http_server.listen(80)
IOLoop.instance().start()
