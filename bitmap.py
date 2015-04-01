#!/usr/bin/python

from PIL import Image
from board import Board
import colorsys
import sys
import math
import pygame
import time

im = Image.open(sys.argv[1])


#px = im.load()


pygame.init()
board = Board()


degree = 0
while True:
    px = im.rotate(degree).load()
    degree += 1
    for x in xrange(57):
        for y in xrange(45):
            try:
                r, g, b, a = px[x,y]
                #print r, g, b
                board.set_light(x, y, (r, g, b))
            except:
                pass

    board.display()
    board.send_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.025)



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.01)


