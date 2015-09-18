
try:
    import pygame
except:
    pass
import psu
import socket
import struct
import logger


class Board(object):
    def __init__(self, size=(600,490), host=('127.0.0.1', 1337), width=57, height=44, use_pygame=True):
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
        self.last_buf = b''
        try:
            self.tcp_sock.connect(host)
        except socket.error:
            self.tcp_sock = None
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

    def send_board(self):
        buf = b''
        for x in range(len(self.lights)):
            for y in range(len(self.lights[x])):
                r, g, b = self.lights[x][y]
                buf += struct.pack('>BBB', r, g, b)
        self.last_buf = buf
        try:
            if self.tcp_sock is not None:
                self.tcp_sock.send(buf)
        except:
            logger.warn("Lights TCP connection died")
            self.tcp_sock = None
            # try reconnect?
            pass

        self.display()

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

