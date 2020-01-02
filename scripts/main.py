import tornado.ioloop
import tornado.web

from login import LoginHandler

app = tornado.web.Application([
    (r"/login",LoginHandler)
])


if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    print("app start at 8888")