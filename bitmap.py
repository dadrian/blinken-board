#!/usr/bin/python

from PIL import Image
from PIL import ImageFilter
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
    px = im.resize((57, 45), Image.ANTIALIAS).filter(ImageFilter.Kernel((3,3), (0, -1, 0, -1, 5, -1, 0, -1, 0))).load()
    if (degree % 90 == 0):
        degree += 0.1
    px = im.rotate(degree).load()
    degree += 15
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


