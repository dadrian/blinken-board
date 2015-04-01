
import pygame
import psu
import socket
import struct



class Board(object):
    def __init__(self, size=(600,490)):
        self.screen = pygame.display.set_mode(size)
        self.screen.fill((0, 0, 0))
        self.lights = []
        for x in xrange(57):
            self.lights.append([])
            for y in xrange(45):
                self.lights[x].append((0, 0, 0))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    def set_light(self, x, y, color):
        self.lights[x][y] = color
        pygame.draw.circle(self.screen, color, (x*10+20, y*10+20), 4)

    def display(self):
        pygame.display.flip()


    def send_board(self):
        for x in xrange(len(self.lights)):

            # x = (psu_id*7 + 8) - (strand_id)

            psu_id = (x-1) / 7
            strand_id = (psu_id*7 + 8) - x
            if x == 0:
                psu_id = 0
                strand_id = 8


            data = '0401dc4a0100080100'.decode('hex') + '00000000'.decode('hex')
            data += struct.pack('>I', strand_id)
            buf = ''
            for y in xrange(len(self.lights[x])):
                r, g, b = self.lights[x][y]
                buf += struct.pack('>BBB', r, g, b)


            data += struct.pack('>I', len(buf))
            data += psu.extra_buf[psu_id]  # weird extra 3 bytes, not sure what it's for yet, seems psu-specific but not an ID?
            data += buf

            # construct UDP packet
            #udp = dpkt.udp.UDP(sport=44280, dport=6038, data=data)
            self.socket.sendto(data, (psu.dest_ips[psu_id], 6038))

