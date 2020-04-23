import tornado.ioloop
import tornado.web
import tornado.httpserver
import os
path = os.sys.path[0]
os.chdir(path)
from login import LoginHandler
from dataMgr import DataMgrHandler
from signInSys import SignInSysHandler
from mailSystem import MailSystemHandler
from helper import HelperHandler
from longConnectHandler import LongConnectHandler

setting = {
    "static_path": os.path.join(os.path.dirname(__file__),"static")
}
print(setting["static_path"])
app = tornado.web.Application([
    (r"/login",LoginHandler),
    (r"/data",DataMgrHandler),
    (r"/signIn",SignInSysHandler),
    (r"/mail",MailSystemHandler),
    (r"/helper",HelperHandler),
    (r"/longConnect",LongConnectHandler)
],**setting)

server = tornado.httpserver.HTTPServer(app, ssl_options = {
    "certfile": os.path.join(os.path.abspath("."),"cert.crt"),
    "keyfile": os.path.join(os.path.abspath("."), "key.key")
})

if __name__ == "__main__":
    # app.listen(8888)
    # print("app start at 8888")
    # tornado.ioloop.IOLoop.current().start()
    server.listen(8888)
    print("app start at 8888")
    tornado.ioloop.IOLoop.current().start()
    