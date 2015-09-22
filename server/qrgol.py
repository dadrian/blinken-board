

from qr import QR
from gameoflife import GameOfLife
from board import Board

# shows the QR code animation, then turns it into a game of life animation
class QRtoGOL(object):
    def __init__(self, board, url, qr_wait_frames=None):
        self.qr = QR(board, url)
        if qr_wait_frames is not None:
            self.qr.wait_frames = qr_wait_frames
        self.game = GameOfLife(board, self.qr.matrix)

    def frames(self):
        yield from self.qr.frames()
        # intermediate? better transition?
        first = True
        for f in self.game.frames():
            if first:
                for i in range(20*3):
                    yield f
                first = False
            yield f

if __name__ == '__main__':
    import time
    board = Board()
    q = QRtoGOL(board, "http://wallhacks.xyz/#Vf4aaeja8", qr_wait_frames=30*5)

    for f in q.frames():
        board.display()
        time.sleep(1/20.0)

