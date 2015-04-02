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

pygame.init()
board = Board()

qr = qrcode.QRCode(
    version=5,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(sys.argv[1])
qr.make(fit=True)
matrix = qr.get_matrix()
size = len(matrix)
x_offset = (57 - size) / 2
y_offset = (45 - size) / 2

while True:
    #px = im.resize((45, 45), Image.ANTIALIAS).filter(ImageFilter.Kernel((3,3), (0, -1, 0, -1, 5, -1, 0, -1, 0))).rotate(degree).load()
    #px = im.rotate(degree).load()
    #degree += 1
    for x in xrange(57):
        for y in xrange(45):
            try:
                if matrix[x][y]:
                    r, g, b = (0, 0, 255)
                else:
                    r, g, b = (255, 255, 0)
                board.set_light(x+x_offset, y+y_offset, (r, g, b))
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


