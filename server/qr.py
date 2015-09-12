
import qrcode
import random

class QR(object):
    def __init__(self, board, url):
        self.board = board
        self.url = url

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
        for x in range(90*30):
            yield


if __name__ == '__main__':
    from board import Board
    import time
    board = Board(use_pygame=True)
    qr = QR(board, 'http://wallhacks.xyz/#VfOkqH6z7Ant')
    for f in qr.frames():
        board.display()
        time.sleep(0.015)

