#!/usr/bin/python


import pygame
import sys
import time
import dpkt
import socket
import struct

import psu
from board import Board


pygame.init()
board = Board()

# actually only 44x57, but the diagonal makes it 45x57, where the diagonal is always off
for x in xrange(57):
    for y in xrange(45):
        board.set_light(x, y, (0, 0, 255))

    board.display()



def parse_pkt(board, psu_id, pkt):
    strand_id, bulbs_len, = struct.unpack('>II', pkt[13:21])

    for bulb_id in xrange(0, bulbs_len/3):
        r, g, b, = struct.unpack('>BBB', pkt[24+bulb_id*3:27+bulb_id*3])
        y = bulb_id
        x = (psu_id*7 + 8) - (strand_id)

        # Might seem weird, but basically the left-most PSU (id=0)
        # has 8 strands, but all the others have 7
        # (for a total of 57)
        #
        #0, 8 => 0
        #...
        # , 1 => 7
        #1, 7 => 8
        # , 6 => 9
        # , 5 => 10
        # , 4 => 11
        # , 3 => 12
        # , 2 => 13
        # , 1 => 14
        #2, 7 => 15

        try:
            board.set_light(x, y, (r, g, b))
        except Exception:
            print 'Error: %d %d %d => %d, %d' % (psu_id, bulb_id, strand_id, x, y)
            sys.exit(1)


    board.display()



f = open(sys.argv[1], 'r')
pcap = dpkt.pcap.Reader(f)

initial_ts = None
initial_rt = None
def wait_for(ts):
    global initial_ts
    global initial_rt

    if initial_ts is None:
        initial_ts = ts
        initial_rt = time.time()
        return

    offset = (ts - initial_ts)
    sleep_time = (offset + initial_rt) - time.time()
    if sleep_time < 0.01:
        return

    time.sleep(sleep_time)

#dest_psu_ips = ['10.4.57.127', '10.4.57.131', '10.4.57.134', '10.4.57.120', '10.4.57.133', '10.4.132.113', '10.4.163.250', '10.4.135.141']
dest_psu_addrs = [socket.inet_aton(x) for x in psu.dest_ips]


for ts, buf in pcap:

    eth = dpkt.ethernet.Ethernet(buf)
    if eth.type == dpkt.ethernet.ETH_TYPE_IP:
        ip = eth.data
        if ip.p == dpkt.ip.IP_PROTO_UDP:
            udp = ip.data
            #if ip.src == socket.inet_aton("10.1.3.100") and udp.dport == 6038:
            if udp.dport == 6038:
                wait_for(ts)
                parse_pkt(board, dest_psu_addrs.index(ip.dst), udp.data)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    #time.sleep(.05)



while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.01)



