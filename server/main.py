import asyncio
import websockets
import websockets.uri
import posixpath

class WebsocketRoute(object):

    def __init__(self, path):
        self._path = path

    def matches(self, request_path):
        if posixpath.dirname(request_path) != posixpath.dirname(self._path):
            return False
        if posixpath.basename(request_path) != posixpath.basename(self._path):
            return False
        return True

    def __call__(self, f):
        def wrapped_f(websocket):
            print("calling function for path {}".format(self._path))
            f(websocket)
        return wrapped_f

class WebsocketServer(object):

    def __init__(self, *args, **kwargs):
        self._routes = list()

    def route(self, path):
        route = WebsocketRoute(path)
        self._routes.append(route)
        return route

    def get_router(self):

        @asyncio.coroutine
        def do_routing(websocket, path):
            for handler in self._routes:
                print("incoming path {}".format(path))
                if handler.matches(path):
                    handler(websocket)
                    print("success")
                    return
            raise NotImplemented
        return do_routing


server = WebsocketServer()

@server.route('/testpath')
@asyncio.coroutine
def hello(websocket):
    name = yield from websocket.recv()
    print("< {}".format(name))
    print(path)
    greeting = "Hello {}!".format(name)
    yield from websocket.send(greeting)
    print("> {}".format(greeting))


start_server = websockets.serve(server.get_router(), 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
