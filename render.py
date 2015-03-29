#!/usr/bin/python


import pygame
import sys
import time
import dpkt
import socket
import struct

class Board(object):
    def __init__(self, size=(700, 700)):
        self.screen = pygame.display.set_mode(size)
        self.screen.fill((0, 0, 0))

    def set_light(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x*10+20, y*10+20), 4)

    def display(self):
        pygame.display.flip()


pygame.init()
board = Board()



for x in xrange(64):
    for y in xrange(64):
        board.set_light(x, y, (0, 0, 255))


    board.display()



def parse_pkt(board, psu_id, pkt):
    strand_id, bulbs_len, = struct.unpack('>II', pkt[13:21])

    for bulb_id in xrange(0, bulbs_len/3):
        r, g, b, = struct.unpack('>BBB', pkt[24+bulb_id*3:27+bulb_id*3])
        x = (psu_id * 8) + (strand_id - 1)
        y = bulb_id
        board.set_light(x, y, (r, g, b))


    board.display()


f = open(sys.argv[1], 'r')
pcap = dpkt.pcap.Reader(f)

for ts, buf in pcap:

    eth = dpkt.ethernet.Ethernet(buf)
    if eth.type == dpkt.ethernet.ETH_TYPE_IP:
        ip = eth.data
        if ip.p == dpkt.ip.IP_PROTO_UDP:
            udp = ip.data
            if ip.src == socket.inet_aton("10.1.3.100") and udp.dport == 6038:
                parse_pkt(board, 0, udp.data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    #time.sleep(.05)
