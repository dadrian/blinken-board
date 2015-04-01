from gevent import monkey; monkey.patch_all()
from ws4py.websocket import WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

class EchoWebSocket(WebSocket):
    def received_message(self, message):
        print len(message.data)
        #self.send(message.data, message.is_binary)

server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=EchoWebSocket))
server.serve_forever()
