#!/usr/bin/python

import time
import numpy as np
import cv2

# needs opencv compiled with ffmpeg support:
# cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=OFF -D WITH_QT=ON -D WITH_OPENGL=ON ../
# make && sudo make install && cd modules/python2 && make && sudo make install   (should produce /usr/local/lib/python2.7/dist-packages/cv2.so)

import sys
from board import Board
import pygame

pygame.init()
#board = Board(host=('141.212.141.3',1337))
board = Board()

for x in xrange(57):
    for y in xrange(44):
        board.set_light(x, y, (255, 255, 0))

board.display()
board.send_board()

#cap = cv2.VideoCapture(0)   # webcam :)
if len(sys.argv) > 1:
    cap = cv2.VideoCapture(sys.argv[1])

while(cap.isOpened()):
    ret, frame = cap.read()
    if not(ret):
        break


    scale = cv2.resize(frame, (57, 45))

    for x in xrange(57):
        for y in xrange(44):
            try:
                b, g, r = scale[y][x]
                board.set_light(x, y, (r, g, b))
            except:
                pass

    board.display()
    board.send_board()

    #cv2.imshow('frame', scale)
    cv2.waitKey(25)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    time.sleep(0.015)


cap.release()
cv2.destroyAllWindows()
