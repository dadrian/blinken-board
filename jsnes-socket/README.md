JSNES+websocket
=====

Edit source/socket-launcher.js with the URL of your websocket server.

Run some local test servers:

    $ python socket-server.py
    $ python -m SimpleHTTPServer 8000

Visit http://localhost:8000.

Your websocket server will receive a png of each frame.
