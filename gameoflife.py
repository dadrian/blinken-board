#!/usr/python


from board import Board
import random
import time
from qr import QR


lights = Board(host=('141.212.141.4', 1337))
#lights = Board()

qr = QR(lights, 'http://wallhacks.xyz/#VfcgOCkL0cq')


WIDTH = 57
HEIGHT = 44

b = {}


for x in range(WIDTH):
    for y in range(HEIGHT):
        b[x,y] = 0
        b_x = x - qr.x_offset
        b_y = y - qr.y_offset
        if (b_x > 0 and b_x < len(qr.matrix)) and (b_y >0 and b_y < len(qr.matrix[0])):
            if qr.matrix[b_x][b_y]:
                b[x,y] = 1

def copy_board(b):
    ret = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            ret[x,y] = b[x,y]
    return ret

def write_board(lights, b):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = (0, 0, 0)
            if b[x,y]:
                color = (255, 255, 255)
            lights.set_light(x, y, color)

def write_board_diff(lights, b, new_b, pct):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            n = 0
            if b[x,y]:
                n = 255
                if new_b[x,y]==0:
                    n = (255 - int(pct*255))
            if not(b[x,y]) and new_b[x,y]:
                n = int(pct*255)
            color = (n, n, n)
            lights.set_light(x, y, color)



def wrap(n,m):
    if n < 0:
        return n + m
    return n % m

def count_live_neighbors(b, x, y):
    live = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i==0 and j==0):
                continue
            live += b[wrap(x+i,WIDTH),wrap(y+j,HEIGHT)]

    return live


def do_generation(b):
    #new_b = copy_board(b)
    new_b = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            neighbors = count_live_neighbors(b, x, y)
            #Any live cell with fewer than two live neighbours dies, as if caused by under-population.
            #Any live cell with more than three live neighbours dies, as if by overcrowding.
            if b[x,y]==1 and (neighbors < 2 or neighbors > 3):
                # die
                new_b[x,y] = 0

            #Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
            elif b[x,y]==0 and neighbors == 3:
                # birth
                new_b[x,y] = 1
            else:
                # survive
                new_b[x,y] = b[x,y]

    return new_b


anim = -1
while True:
    write_board(lights, b)
    lights.send_board()

    new_b = do_generation(b)
    for i in range(anim+1):

        write_board_diff(lights, b, new_b, float(i)/anim)
        lights.send_board()
        time.sleep(0.05)


    time.sleep(1/20.0)
    b = new_b
