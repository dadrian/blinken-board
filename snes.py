#!/usr/bin/python

from board import Board
from PIL import ImageFilter
from PIL import Image
import dpkt
import pygame
import time
import colorsys
import sys
import math
import io
import StringIO
import socket
import struct


from gevent import monkey; monkey.patch_all()
from ws4py.websocket import WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

#pygame.init()
#board = Board()

ctr = 0
n = 0
board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
remote_host = ('141.212.111.193', 9009)

board_socket.connect(remote_host)


class EchoWebSocket(WebSocket):
    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, message):
        global board
        global n
        global board_socket
        global remote_host

        print 'pkt %d' % n
        n += 1
        n %= 3
        if n != 0:
            return

        img_data = message.data.split(',')[1].decode('base64')
        img = Image.open(StringIO.StringIO(img_data))
        #img.thumbnail((57, 45), Image.ANTIALIAS)
        bsize = 8
        small_img = img.crop((bsize, bsize, 256-bsize, 240-bsize)).resize((57, 45), Image.ANTIALIAS)#.filter(ImageFilter.Kernel((3,3), (0, -0.25, 0, -0.25, 2, -0.25, 0, -0.25, 0)))

        # Convert it to a png to ship across the network
        #small_img_png = StringIO.StringIO()
        #small_img.save(small_img_png, "PNG", optimize=True)
        #png_data = small_img_png.getvalue()
        #small_img_png.close()

        # convert to bmp
        small_img_bmp = StringIO.StringIO()
        r, b, g, a = small_img.split()
        bmp_img = Image.merge("RGB", (r, g, b))
        bmp_img.save(small_img_bmp, "BMP")
        bmp_data = small_img_bmp.getvalue()
        small_img_bmp.close()

        print len(img_data), len(bmp_data)

        pkt = struct.pack('!H', len(bmp_data)) + bmp_data
        #pkt = struct.pack('!H', len(png_data)) + png_data
        try:
            board_socket.send(pkt)
        except:
            print 'Reconnecting to remote host...'
            board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            board_socket.connect(remote_host)

#        px = small_img.load()
#        for x in xrange(57):
#            for y in xrange(45):
#                try:
#                    r, g, b, a = px[x,y]
#                    board.set_light(x, y, (r, g, b))
#                except:
#                    pass
#
#        board.display()
#        board.send_board()
#
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                pygame.quit();
#                sys.exit();
#        #time.sleep(0.025)
#
#
        #self.send(message.data, message.is_binary)

server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
server.serve_forever()




