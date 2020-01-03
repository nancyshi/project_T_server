import tornado.ioloop
import tornado.web
import os

from login import LoginHandler
path = os.sys.path[0]
os.chdir(path)

app = tornado.web.Application([
    (r"/login",LoginHandler)
])


if __name__ == "__main__":
    app.listen(8888)
    print("app start at 8888")
    tornado.ioloop.IOLoop.current().start()
    