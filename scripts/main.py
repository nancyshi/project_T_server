import tornado.ioloop
import tornado.web
import os
path = os.sys.path[0]
os.chdir(path)
from login import LoginHandler
from dataMgr import DataMgrHandler
from signInSys import SignInSysHandler
from mailSystem import MailSystemHandler
from helper import HelperHandler


app = tornado.web.Application([
    (r"/login",LoginHandler),
    (r"/data",DataMgrHandler),
    (r"/signIn",SignInSysHandler),
    (r"/mail",MailSystemHandler),
    (r"/helper",HelperHandler)
])
print (path)

if __name__ == "__main__":
    app.listen(8888)
    print("app start at 8888")
    tornado.ioloop.IOLoop.current().start()
    