import tornado.web
class BaseHttpHandler(tornado.web.RequestHandler):
    def __init__(self,application,request,**kw):
        super().__init__(application,request,**kw)
        self.setDefaultHeader()

    def setDefaultHeader(self):
        self.set_header('Access-Control-Allow-Origin',"*")
        self.set_header("Access-Control-Allow-Headers","x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        self.write("hello")