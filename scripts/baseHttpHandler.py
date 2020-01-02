import tornado.web
class BaseHttpHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello")