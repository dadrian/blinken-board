#!/usr/bin/python

from board import Board
from PIL import Image
import dpkt
import pygame
import time
import colorsys
import sys
import math
import io
import StringIO


from gevent import monkey; monkey.patch_all()
from ws4py.websocket import WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

pygame.init()
board = Board()

ctr = 0
n = 0

class EchoWebSocket(WebSocket):

    def received_message(self, message):
        global board
        global n

        n = 1 - n
        if n == 0:
            return

        img_data = message.data.split(',')[1].decode('base64')
        img = Image.open(StringIO.StringIO(img_data))
        #img.thumbnail((57, 45), Image.ANTIALIAS)
        px = img.resize((57, 45), Image.ANTIALIAS).load()
        for x in xrange(57):
            for y in xrange(45):
                try:
                    r, g, b, a = px[x,y]
                    board.set_light(x, y, (r, g, b))
                except:
                    pass

        board.display()
        board.send_board()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit();
        #time.sleep(0.025)


        #self.send(message.data, message.is_binary)

server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
server.serve_forever()




