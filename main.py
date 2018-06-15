import tornado.ioloop
import tornado.web
import logging
from mission_handler import *
from tornado.log import *

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/mission',MissionHandler)
    ])

if __name__ == "__main__":
    handler = logging.FileHandler('log/main.log')
    app_log = logging.getLogger("tornado.application")
    enable_pretty_logging()
    app_log.addHandler(handler)
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
