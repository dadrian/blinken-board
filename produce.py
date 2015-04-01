#!/usr/bin/python

from board import Board
import dpkt
import pygame
import time
import colorsys
import sys
import math


pygame.init()
board = Board()


while True:

    t = (time.time()/15.0) % 1
    for x in xrange(57):
        for y in xrange(45):
            #r, g, b, = colorsys.hsv_to_rgb((t+ x/(300.0*(0.3*math.sin(t*2*math.pi-0.4)+0.5)) + math.cos(2*math.pi*y/100.0))%1, 1, 1)
            r, g, b, = colorsys.hsv_to_rgb((t + x/300.0 + y/400.0) % 1, 1, 1)
            board.set_light(x, y, (int(r*255), int(g*255), int(b*255)))

    board.display()
    board.send_board()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();

    time.sleep(0.025)






