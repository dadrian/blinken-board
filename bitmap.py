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
board = Board(host=('141.212.141.4', 1337))


WIDTH = 57
HEIGHT = 44

ratio = float(im.size[0]) / im.size[1]
print(im.size)
print('ratio: %f' % (ratio))

resize_w = WIDTH
resize_h = HEIGHT
left_offset = 0
top_offset = 0

if (ratio * HEIGHT) < WIDTH:
    print('vertically limitted')
    resize_w = int(HEIGHT * ratio)
    resize_h = HEIGHT
    left_offset = (WIDTH - resize_w) / 2
else:
    print('horizontal limitted')
    resize_w = WIDTH
    resize_h = int(WIDTH /  ratio)
    top_offset = (HEIGHT - resize_h) / 2

print('resizing to (%d, %d) top: %d, left: %d' % (resize_w, resize_h, top_offset, left_offset))

#degree = 0
while True:


    px = im.resize((resize_w, resize_h), Image.ANTIALIAS).load() #filter(ImageFilter.Kernel((3,3), (0, -1, 0, -1, 5, -1, 0, -1, 0))).load()
    #if (degree % 90 == 0):
    #    degree += 0.1
    #px = im.rotate(degree).load()
    #degree += 15
    for x in xrange(WIDTH):
        for y in xrange(HEIGHT):
            try:

                im_x = x - left_offset
                im_y = y - top_offset
                if im_x < resize_w and im_y < resize_h:
                    r = px[im_x, im_y][0]
                    g = px[im_x, im_y][1]
                    b = px[im_x, im_y][2]
                    if len(px[im_x, im_y]) > 3:
                        a = px[im_x, im_y][3]
                        r *= (a/255.0)
                        g *= (a/255.0)
                        b *= (a/255.0)
                else:
                    r, g, b = (0, 0, 0)

                board.set_light(x, y, (int(r), int(g), int(b)))
            except:
                pass

    #board.display()
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


