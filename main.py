import tornado.ioloop
# import tornado.web
import tornado.websocket
# import subprocess

from app import App

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    app_cache = App()
    ping_interval = 0

    def check_origin(self,remote_address):
        # CORS
        return True

    def open(self):
        self.app_cache.register(self)

    def on_close(self):
        # print("connection closing")
        self.app_cache.logout(self)

    async def on_message(self, message):
        await self.app_cache.execute(self, message)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', WebSocketHandler),
        ]
        tornado.web.Application.__init__(self, handlers, websocket_ping_interval=0)


if __name__ == "__main__":
    print("----------Server Started----------")
    app = Application()
    app.listen(8000, address='0.0.0.0')
    # subprocess.call("python3 -u tick.py")
    tornado.ioloop.IOLoop.current().start()
    print("----------Server Stopped----------")
