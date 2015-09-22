#!/usr/python


from board import Board
import random



WIDTH = 57
HEIGHT = 44

def wrap(n,m):
    if n < 0:
        return n + m
    return n % m

class GameOfLife(object):
    # lights is the board.Board() object
    # initial_matrix should be a 2d array (please ensure width/height is big enough
    # anim is number of frames to animate (-1 for no animation)
    def __init__(self, lights=None, initial_matrix=None, width=WIDTH, height=HEIGHT, anim=-1):
        self.b = {}
        self.lights = lights
        self.width = width
        self.height = height
        self.anim = anim
        if (initial_matrix is not None):
            self.init_matrix(initial_matrix)



    def init_matrix(self, matrix):
        x_offset = (self.width - len(matrix)) / 2
        y_offset = (self.height - len(matrix[0])) / 2
        for x in range(self.width):
            for y in range(self.height):
                self.b[x,y] = 0
                b_x = x - x_offset
                b_y = y - y_offset
                if (b_x > 0 and b_x < len(matrix)) and (b_y >0 and b_y < len(matrix[0])):
                    if matrix[b_x][b_y]:
                        self.b[x,y] = 1



    def write_board(self):
        for x in range(self.width):
            for y in range(self.height):
                color = (0, 0, 0)
                if self.b[x,y]:
                    color = (255, 255, 255)
                self.lights.set_light(x, y, color)

    def write_board_diff(new_b, pct):
        for x in range(self.width):
            for y in range(self.height):
                n = 0
                if self.b[x,y]:
                    n = 255
                    if new_b[x,y]==0:
                        n = (255 - int(pct*255))
                if not(self.b[x,y]) and new_b[x,y]:
                    n = int(pct*255)
                color = (n, n, n)
                self.lights.set_light(x, y, color)


    def count_live_neighbors(self, x, y):
        live = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i==0 and j==0):
                    continue
                live += self.b[wrap(x+i,self.width),wrap(y+j,self.height)]

        return live


    def do_generation(self):
        new_b = {}
        for x in range(self.width):
            for y in range(self.height):
                neighbors = self.count_live_neighbors(x, y)
                #Any live cell with fewer than two live neighbours dies, as if caused by under-population.
                #Any live cell with more than three live neighbours dies, as if by overcrowding.
                if self.b[x,y]==1 and (neighbors < 2 or neighbors > 3):
                    # die
                    new_b[x,y] = 0

                #Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
                elif self.b[x,y]==0 and neighbors == 3:
                    # birth
                    new_b[x,y] = 1
                else:
                    # survive
                    new_b[x,y] = self.b[x,y]

        return new_b


    def frames(self):
        while True:
            self.write_board()
            new_b = self.do_generation()
            yield

            for i in range(self.anim+1):
                self.write_board_diff(new_b, float(i)/self.anim)
                yield

            self.b = new_b

if __name__ == '__main__':
    import time
    from qr import QR
    #lights = Board(host=('141.212.141.4', 1337))
    lights = Board()

    qr = QR(lights, 'http://wallhacks.xyz/#VfcgOCkL0cq')
    life = GameOfLife(lights, qr.matrix)

    for f in life.frames():
        lights.send_board()
        time.sleep(0.05)
