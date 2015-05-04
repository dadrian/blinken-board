#!/usr/bin/python

import StringIO
import io
import qrcode
from PIL import Image
from PIL import ImageFilter
from board import Board
import colorsys
import sys
import math
import pygame
import time
import random

pygame.init()
board = Board()

qr = qrcode.QRCode(
    version=6,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=2,
)
qr.add_data(sys.argv[1])
qr.make(fit=True)
matrix = qr.get_matrix()
size = len(matrix)
x_offset = (57 - size) / 2
y_offset = (45 - size) / 2



# Get a list of "on" pixels
indexes = [ (x, y) for x in xrange(len(matrix)) for y in xrange(len(matrix[0])) if matrix[x][y] ]
random.shuffle(indexes)


for x in xrange(57):
    for y in xrange(45):
        board.set_light(x, y, (255, 255, 0))

board.display()
board.send_board()

for x, y in indexes:

    board.set_light(x+x_offset, y+y_offset, (0, 0, 255))

    board.display()
    board.send_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.025)


degree = 0
while True:

    r, g, b = colorsys.hsv_to_rgb((degree+60)/360.0, 1, 1)
    for x in xrange(57):
        for y in xrange(45):
            board.set_light(x, y, (int(r*255), int(g*255), int(b*255)))

    r, g, b = colorsys.hsv_to_rgb((degree+240)/360.0, 1, 1)
    for x in xrange(57):
        for y in xrange(45):
            try:
                if matrix[x][y]:
                    board.set_light(x+x_offset, y+y_offset, (int(r*255), int(g*255), int(b*255)))
            except:
                pass

    board.display()
    board.send_board()
    degree += 5
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.025)


