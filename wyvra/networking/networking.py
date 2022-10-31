import socket

from _thread import *
import threading

class networking():
    """
    The request handler class for our MUD.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    server = None

    def __init__(self, host="0.0.0.0", port=4444):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(5)
        self.server = s
