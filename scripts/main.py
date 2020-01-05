import tornado.ioloop
import tornado.web
import os

from login import LoginHandler
from dataMgr import DataMgrHandler
path = os.sys.path[0]
os.chdir(path)

app = tornado.web.Application([
    (r"/login",LoginHandler),
    (r"/data",DataMgrHandler)
])


if __name__ == "__main__":
    app.listen(8888)
    print("app start at 8888")
    tornado.ioloop.IOLoop.current().start()
    