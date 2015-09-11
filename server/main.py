import asyncio
import websockets
import websockets.uri
import posixpath
import urllib
import re
import time
import struct
import base64
import hmac
import codecs

TOKEN_HMAC_KEY = b'fogBI6ymJDbQCf6KVVr5x14r'
TOKEN_HMAC_TAG_LEN = 5   # bytes
MAX_TOKEN_AGE = 60*10    # seconds

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
from menu import NesMenu
from qr import QR

active_players = 0
in_menu = True
menu = NesMenu()
getscreen_websocks = []

def write_img(board, img):
    px = img.load()
    for x in range(57):
        for y in range(44):
            try:
                colors = px[x,y]
                r = colors[0]
                g = colors[1]
                b = colors[2]
                board.set_light(x, y, (r, g, b))
            except:
                pass



@server.route('/png')
@asyncio.coroutine
def handle_png(websocket):

    global active_players
    global in_menu
    global getscreen_websocks

    #board = Board(use_pygame=False, host=('141.212.111.193', 1337))
    board = Board(use_pygame=True)# host=('127.0.0.1', 1337))
    #board = Board(use_pygame=False)
    qr = None
    idle_frame = None
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

        if active_players > 0:
            idle_frame = None
            if not(in_menu):
                img_data = base64.b64decode(message.split(',')[1])
                img = Image.open(io.BytesIO(img_data))
                bsize = 8   # NES border size
                small_img = img.crop((bsize, bsize, 256-bsize, 240-bsize)).resize((57, 45), Image.ANTIALIAS).filter(ImageFilter.Kernel((3,3), (0, -0.25, 0, -0.25, 2, -0.25, 0, -0.25, 0)))
                write_img(board, small_img)
            else:
                # read image from menu
                small_img = menu.get_image()
                write_img(board, small_img)
        else:
            # Do QR code things, every so often
            if time.gmtime().tm_sec == 0 and time.gmtime().tm_min % 1 == 0 and idle_frame is None:
                print('New QR code animation...')

                tb = struct.pack('>L', int(time.time()))            # get time as 4-byte array
                tag = hmac.new(TOKEN_HMAC_KEY, tb).digest()[0:TOKEN_HMAC_TAG_LEN]    # truncated hmac with secret
                token = base64.urlsafe_b64encode(tb + tag)
                url = 'http://wallhacks.io/#' + str(token, 'ascii')

                print('url: %s' % (url))

                #'http://141.212.111.203:8001/c.html'
                qr = QR(board, url)
                idle_frame = qr.frames()
            if idle_frame is not None:
                try:
                    idle_frame.__next__()
                    board.send_board()
                except StopIteration:
                    idle_frame = None


        #board.display()
        if active_players > 0:
            board.send_board()
            for ws in getscreen_websocks:
                try:
                    yield from ws.send(board.get_last_buf())
                except:
                    getscreen_websocks.remove(ws)

        frames += 1
        tot_frames += 1
        now = time.time()
        if (now - last_time) > 5:
            fps = float(frames) / (now - last_time)
            print("%f FPS, %d total, %d byte frame, in_menu: %s, players: %d" % (fps, tot_frames, len(message), in_menu, active_players))
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

@server.route('/getscreen')
@asyncio.coroutine
def handle_getscreen(websocket):
    # add this caller to the board.send_board queue!
    # so they can see the glory of the board, too
    global getscreen_websocks
    getscreen_websocks.append(websocket)
    print('Adding getscreen listener')
    while True:
        message = yield from websocket.recv()
        if message is None:
            getscreen_websocks.remove(websocket)
            print('Removing getscreen listener')
            break


@server.route('/controller')
@asyncio.coroutine
def handle_controller(websocket):

    global controller_websocks
    global active_players
    global in_menu

    buttons = {'A': False, 'B': False, 'Start': False, 'Select': False, 'Left': False, 'Right': False, 'Up': False, 'Down': False }

    # get token message (first message)
    token = yield from websocket.recv()

    if token is None:
        return

    # validate token
    token_raw = base64.urlsafe_b64decode(token)
    ts = token_raw[0:4]
    tag = token_raw[4:]
    t, = struct.unpack('>L', ts)

    age = int(time.time()) - t
    print('new controller with token %s (%d seconds old)' % (token, age))

    # validate tag
    expected_tag = hmac.new(TOKEN_HMAC_KEY, ts).digest()[0:TOKEN_HMAC_TAG_LEN]
    if not(hmac.compare_digest(tag, expected_tag)):
        #print('Incorrect tag %s (expected %s) for time %d' % (codecs.encode(bytes(tag, 'ascii'), 'hex'), codecs.encode(bytes(expected_tag, 'ascii'), 'hex'), t))
        print('Incorrect tag %s (expected %s) for time %d' % (tag, expected_tag, t))
        yield from websocket.send('!bad_token')
        return

    if (age > MAX_TOKEN_AGE):
        print('token too old')
        yield from websocket.send('!old_token')
        return


    active_players += 1
    if active_players == 1:
        in_menu = True

    while True:
        message = yield from websocket.recv()

        # check for disconnected websocket
        if message is None:
            active_players -= 1
            print('controller websocket closed')
            break

        print('controller: %s' % message)

        key = message[1:]
        if message[0] == '+':
            buttons[key] = True
        elif message[0] == '-':
            buttons[key] = False


        # if we're in a menu, interact with the menu
        if in_menu:
            if message == '+Start':
                # select game
                for ws in controller_websocks:
                    yield from ws.send('>'+menu.current_game())
                in_menu = False
            else:
                if message == '+Right':
                    menu.right()
                elif message == '+Left':
                    menu.left()
        else:
            # send key events to the other listeners
            for ws in controller_websocks:
                yield from ws.send(message)


        #raw = get_hidraw(buttons)
        #print(hex(raw))
        #sock.send(struct.pack('!Q', raw))


start_server = websockets.serve(server.get_router(), '0.0.0.0', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
