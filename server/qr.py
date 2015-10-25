
import qrcode
import random

class QR(object):
    def __init__(self, board, url, wait_frames=50*30):
        self.board = board
        self.url = url
        self.wait_frames = wait_frames  # number of frames to keep the animation at at the end

        qr = qrcode.QRCode(
            version=6,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )

        qr.add_data(url)
        qr.make(fit=True)

        self.matrix = qr.get_matrix()
        size = len(self.matrix)
        self.x_offset = (57 - size) / 2
        self.y_offset = (44 - size) / 2

        # Get a list of "on" pixels, and randomize it
        self.indexes = [ (x, y) for x in range(len(self.matrix)) for y in range(len(self.matrix[0])) if self.matrix[x][y] ]
        random.shuffle(self.indexes)

        # dummy board (maybe they just want the matrix)
        if board is None:
            return

        # initialize board
        for x in range(57):
            for y in range(44):
                self.board.set_light(x, y, (128, 128, 128))



    def frames(self):
        idx = 0
        for x, y in self.indexes:
            self.board.set_light(int(x+self.x_offset), int(y+self.y_offset), (0, 0, 0))

            idx += 1
            if idx % 10 == 0:
                yield  # send board, sleep a bit...repeat

        # maintain this board for a bit
        for x in range(self.wait_frames):
            yield


if __name__ == '__main__':
    from board import Board
    import time
    import sys
    board = Board(use_pygame=True)
    url = 'http://wallhacks.xyz/#VfcgOCskL0cq'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    qr = QR(board, url)
    for f in qr.frames():
        board.display()
        time.sleep(0.015)

