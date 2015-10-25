

import struct
import sun
import time
import logger
from qr import QR
from qrgol import QRtoGOL
import hmac
import base64
from board import Board


TOKEN_HMAC_KEY = b'fogBI6ymJDbQCf6KVVr5x14r'
TOKEN_HMAC_TAG_LEN = 5   # bytes
QR_CODE_PATH = 'http://wallhacks.xyz/'

def main():
    board = Board(use_pygame=False, create_ws=True)
    last_civil = True
    while True:
        if (time.gmtime().tm_sec == 0) and time.gmtime().tm_min % 5 == 0:
            if sun.is_civil_twilight():
                # keep lights off
                if last_civil is False:
                    logger.info('Ending QR display (start of civil twilight)')
                last_civil = True
            else:
                if last_civil is True:
                    logger.info('Starting QR display (end of civil twilight)')
                last_civil = False
                logger.debug('New QR code animation...')

                tb = struct.pack('>L', int(time.time()))            # get time as 4-byte array
                tag = hmac.new(TOKEN_HMAC_KEY, tb).digest()[0:TOKEN_HMAC_TAG_LEN]    # truncated hmac with secret
                token = base64.urlsafe_b64encode(tb + tag)
                url = QR_CODE_PATH + '#' + str(token, 'ascii')

                logger.debug('url: %s' % (url))

                #qr = QRtoGOL(board, url, qr_wait_frames=20*50)
                qr =  get_long_qr_to_gol(board, url, range(7,16), min_generations=60*3*20, qr_wait_frames=20*50)

                for f in qr.frames():
                    board.send_board_ws()
                    time.sleep(1/20.0)
                logger.debug('End of QR/GOL')
        time.sleep(0.5)



if __name__=='__main__':
    logger.setLogLevel(logger.INFO)
    main()
