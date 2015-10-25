

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


# Given the url like 'http://wallhacks.xyz/#Vf4aaeja8' and
# fiddle_offsets = range(716) will yield the url permutations
# 'http://wallhackS.xyz..', 'wallhacKs.xyz, hacKS.xyz.. etc
def permutations(url, fiddle_offsets):

    for i in range(2**len(fiddle_offsets)):
        tmp_url = url
        for idx, offset in enumerate(fiddle_offsets):
            if ((1 << idx) & i):
                tmp_url = tmp_url[0:offset] + tmp_url[offset].upper() + tmp_url[offset+1:]
        yield tmp_url

#Given a url like 'http://wallhacks.xyz/#Vf4aaeja8' and fiddle_offsets = range(7,16)
# this will permute the url ('http://wAlLHAckS.xyz/#Vf4aaeja8') until it generates
# a QR code that when set as an initial seed of game of life runs for at least
# min_generations before hitting a loop
def get_long_qr_to_gol(board, url, fiddle_offsets, min_generations=1000, qr_wait_frames=None):
    max_gens = 0
    max_url = url
    for fuzz_url in permutations(url, fiddle_offsets):
        qr = QR(None, fuzz_url)
        gol = GameOfLife(None, qr.matrix)
        gens = gol.how_many_generations(min_generations)
        print('%s: %d generations' % (fuzz_url, gens))
        if gens >= min_generations:
            return QRtoGOL(board, fuzz_url, qr_wait_frames=qr_wait_frames)
        if gens > max_gens:
            max_gens = gens
            max_url = fuzz_url

    return QRtoGOL(board, max_url, qr_wait_frames=qr_wait_frames)



if __name__ == '__main__':
    import time
    import sys
    board = Board()
    #q = QRtoGOL(board, "http://wallhacks.xyz/#Vf4aaeja8", qr_wait_frames=30*5)


    #for url in permutations('http://wallhacks.xyz/#Vf4aaeja8', range(7,9)):
    #    print(url)

    q = get_long_qr_to_gol(board, 'http://wallhacks.xyz/#Vfm587fe9', range(7,16), min_generations=60*3*20, qr_wait_frames=20*5)
    sys.exit(0)

    for f in q.frames():
        board.display()
        time.sleep(1/20.0)

