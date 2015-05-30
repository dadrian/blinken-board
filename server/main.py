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
        print("inside of call")
  
        @asyncio.coroutine
        def wrapped_f(websocket):
            print('calling function for route {}'.format(self._path._raw_path))
            yield from f(websocket)
        self._callback = wrapped_f
        return wrapped_f


class WebsocketServer(object):

    def __init__(self, *args, **kwargs):
        self._routes = list()

    def route(self, path):
        route = WebsocketRoute(path)
        self._routes.append(route)
        print('inside of route')
        return route

    def get_router(self):

        @asyncio.coroutine
        def do_routing(websocket, path):
            for handler in self._routes:
                print("incoming url {}".format(path))
                url_parts = urllib.parse.urlparse(path)
                print("incoming path {}", url_parts.path)              
                if handler.matches(url_parts.path):
                    res = yield from handler._callback(websocket)
                    print("success")
                    return res
            raise NotImplemented
        return do_routing


server = WebsocketServer()


@server.route('/testpath')
@asyncio.coroutine
def hello(websocket):
    print('hello')
    name = yield from websocket.recv()
    print("< {}".format(name))
    greeting = "Hello {}!".format(name)
    yield from websocket.send(greeting)
    print("> {}".format(greeting))

from board import Board
from PIL import ImageFilter
from PIL import Image
import base64
import io
import time

active_players = 1

@server.route('/png')
@asyncio.coroutine
def handle_png(websocket):

    global active_players

    #board = Board(use_pygame=False, host=('141.212.111.193', 1337))
    #board = Board(use_pygame=False, host=('141.212.141.3', 1337))
    board = Board(use_pygame=False)
    print('pngpng')
    frames = 0
    tot_frames = 0
    last_time = time.time()
    printed_msg = 0
    while True:
        message = yield from websocket.recv()
        if message is None:
            # closed websocket
            print("Closed png websock")
            break
        if (printed_msg % 1000) == 0:
            print(len(message))
            #print(message)

        printed_msg += 1

        if True:
            img_data = base64.b64decode(message.split(',')[1])
            img = Image.open(io.BytesIO(img_data))
            #img.thumbnail((57, 45), Image.ANTIALIAS)
            bsize = 8
            small_img = img.crop((bsize, bsize, 256-bsize, 240-bsize)).resize((57, 45), Image.ANTIALIAS).filter(ImageFilter.Kernel((3,3), (0, -0.25, 0, -0.25, 2, -0.25, 0, -0.25, 0)))

            px = small_img.load()
            for x in range(57):
                for y in range(44):
                    try:
                        r, g, b = px[x,y]
                        board.set_light(x, y, (r, g, b))
                    except:
                        pass

            #board.display()
            if active_players > 0:
                board.send_board()

        frames += 1
        tot_frames += 1
        now = time.time()
        if (now - last_time) > 5:
            fps = float(frames) / (now - last_time)
            print("%f FPS, %d total" % (fps, tot_frames))
            last_time = now
            frames = 0

        #time.sleep(0.025)

import socket
import struct

button_hid = {'A':      (0x0000000000200000, False), \
              'B':      (0x0000000000400000, False), \
              'Start':  (0x0000000000002000, False), \
              'Select': (0x0000000000001000, False), \
              'Right':  (0x0000008000000000, False), \
              'Down':   (0x0000000080000000, False), \
              'Left':   (0x0000000100000000, True), \
              'Up':     (0x0000000001000000, True)}
                # except left and up should clear those bits

def get_hidraw(buttons):
     # 01 7f 7f 7f 7f 0f 00 00
    out = 0x017f7f7f7f0f0000
    for k in buttons.keys():
        if buttons[k]:
            mask, rev = button_hid[k]
            out |= mask
            if rev:
                out &= ~mask
    return out


controller_websocks = []

@server.route('/getcontrols')
@asyncio.coroutine
def handle_getcontrols(websocket):
    global controller_websocks
    controller_websocks.append(websocket)
    while True:
        message = yield from websocket.recv()
        if message is None:
            controller_websocks.remove(websocket)
            print('controller listener websocket closed')
            break

@server.route('/controller')
@asyncio.coroutine
def handle_controller(websocket):

    global controller_websocks
    global active_players

    hit_start = False

    buttons = {'A': False, 'B': False, 'Start': False, 'Select': False, 'Left': False, 'Right': False, 'Up': False, 'Down': False }
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    #sock.connect(('127.0.0.1', 8888))

    while True:
        message = yield from websocket.recv()
        if message is None:
            active_players -= 1
            print('controller websocket closed')
            break

        if not(hit_start) and message == '+Start':
            hit_start = True
            active_players += 1

        print('controller: %s' % message)
        key = message[1:]
        if message[0] == '+':
            buttons[key] = True
        elif message[0] == '-':
            buttons[key] = False

        for ws in controller_websocks:
            yield from ws.send(message)


        #raw = get_hidraw(buttons)
        #print(hex(raw))
        #sock.send(struct.pack('!Q', raw))


start_server = websockets.serve(server.get_router(), '0.0.0.0', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
