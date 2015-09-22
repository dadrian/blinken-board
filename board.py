
try:
    import pygame
except:
    pass
import psu
import socket
import struct
import logger
import time
from websocket import create_connection
import base64


class Board(object):
    def __init__(self, size=(600,490), host=('127.0.0.1', 1337), width=57, height=44, use_pygame=True, reconnect_interval=30, create_ws=False):
        self.screen = None
        if use_pygame:
            self.screen = pygame.display.set_mode(size)
            self.screen.fill((0, 0, 0))
        self.lights = []
        for x in range(width):
            self.lights.append([])
            for y in range(height):
                self.lights[x].append((0, 0, 0))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.tcp_sock.settimeout(5)
        self.last_buf = b''
        self.host = host
        self.last_reconnect = time.time()
        self.reconnect_interval = reconnect_interval
        try:
            self.tcp_sock.connect(host)
            logger.debug('Connected to %s' % (str(host)))
        except socket.error:
            logger.warn('Could not connect to %s' % (str(host)))
            self.tcp_sock = None
            pass

        try:
            if create_ws:
                self.ws = create_connection('ws://localhost:8765/raw_board')
                logger.trace('created websocket for board')
        except:
            logger.warn('failed to create websocket')
            pass



    def reconnect_tcp(self):
        now = time.time()
        if (now - self.last_reconnect) < self.reconnect_interval:
            return
        self.last_reconnect = now

        logger.debug('reconnecting to %s' % (str(self.host)))
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.tcp_sock.settimeout(5)
        try:
            self.tcp_sock.connect(self.host)
            logger.info('Reconnected to lights %s' % (str(self.host)))
        except socket.error:
            self.tcp_sock = None
            logger.debug('Failed to reconnect to %s' % (str(self.host)))
            pass

    def set_light(self, x, y, color):
        self.lights[x][y] = color
        if self.screen is not None:
            pygame.draw.circle(self.screen, color, (x*10+20, y*10+20), 4)

    def display(self):
        if self.screen is not None:
            pygame.display.flip()

    def get_last_buf(self):
        return self.last_buf

    def serialize_board(self):
        buf = b''
        for x in range(len(self.lights)):
            for y in range(len(self.lights[x])):
                r, g, b = self.lights[x][y]
                buf += struct.pack('>BBB', r, g, b)
        return buf

    def send_board(self):
        buf = self.serialize_board()
        self.send_buf_tcp(buf)
        self.display()

    def send_board_ws(self):
        buf = self.serialize_board()
        logger.info('buf len: %d' % (len(buf)))
        if len(buf) == 0:
            return
        #self.ws.send(buf)
        self.ws.send(base64.b64encode(buf))

    def send_buf_tcp(self, buf):
        self.last_buf = buf
        try:
            if self.tcp_sock is not None:
                self.tcp_sock.send(buf)
            else:
                self.reconnect_tcp()
        except Exception as e:
            logger.warn("Lights TCP connection died: %s" % (str(e)))
            self.tcp_sock = None
            self.reconnect_tcp()
            # try reconnect?
            pass


    def send_board_udp(self):
        for x in range(len(self.lights)):

            # x = (psu_id*7 + 8) - (strand_id)

            psu_id = (x-1) / 7
            strand_id = (psu_id*7 + 8) - x
            if x == 0:
                psu_id = 0
                strand_id = 8


            data = '0401dc4a0100080100'.decode('hex') + '00000000'.decode('hex')
            data += struct.pack('>I', strand_id)
            buf = ''
            for y in range(len(self.lights[x])):
                r, g, b = self.lights[x][y]
                buf += struct.pack('>BBB', r, g, b)


            data += struct.pack('>I', len(buf))
            data += psu.extra_buf[psu_id]  # weird extra 3 bytes, not sure what it's for yet, seems psu-specific but not an ID?
            data += buf

            # construct UDP packet
            #udp = dpkt.udp.UDP(sport=44280, dport=6038, data=data)
            self.socket.sendto(data, (psu.dest_ips[psu_id], 6038))

