import asyncio
import websockets
import websockets.uri
import posixpath
import urllib
import re

def path_to_list(path):
    base = posixpath.basename(path)
    tree = posixpath.dirname(path)
    parts = list()
    while base:
        parts.append(base)
        base = posixpath.basename(tree)
        tree = posixpath.dirname(tree)
    return reversed(parts)

class RoutePath(object):
    
    def __init__(self, path):
        self._raw_path = path
        self._parts = path_to_list(path)
        regex_str = '\/' + '\/'.join(
 	        [RoutePath.regex_for_part(part) for part in self._parts]
        )
        self._variables = [part[1:] for part in self._parts if part[0] == ':']
        self._regex = re.compile(regex_str)
        
    def matches(self, candidate_path):
        m = self._regex.fullmatch(candidate_path)
        if m:
            context = dict()
            context['__raw_path'] = candidate_path
            for idx, name in enumerate(self._variables):
                context[name] = m.group(idx)
            return context
        return None
    
    @classmethod
    def regex_for_part(cls, part):
        if len(part) == 0:
            raise Exception
        if part[0] == ':':
            return '(.+)'
        return part
                               

class WebsocketRoute(object):

    def __init__(self, path):
        self._path = RoutePath(path)
    
    def matches(self, candidate):
        return self._path.matches(candidate)

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
                print("incoming url {}".format(path))
                url_parts = urllib.parse.urlparse(path)
                print("incoming path {}", url_parts.path)              
                if handler.matches(url_parts.path):
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
