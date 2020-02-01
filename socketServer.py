# coding: UTF-8

from websocket_server import WebsocketServer
from debug import INFO


# Called for every client connecting (after handshake)
def new_client(client, server):
    INFO("New client connected and was given id " + str(client['id']))
    server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
    INFO("Client(" + str(client['id']) + ") disconnected")


# Called when a client sends a message
def message_received(client, server, message):
    reply_message = 'Hi! ' + message
    server.send_message(client, reply_message)
    INFO("Client(" + str(client['id']) + ") said: " + message)


class Server:
    def __init__(self, port=9001):
        self._server = WebsocketServer(port=port, host='192.168.100.122')
        self._server.set_fn_new_client(new_client)
        self._server.set_fn_client_left(client_left)
        self._server.set_fn_message_received(message_received)
    
    def target(self):
        self._server.run_forever()
