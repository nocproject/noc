# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP Client library
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
## NOC modules
from clientsocket import STOMPClientSocket
from noc.lib.nbsocket import SocketFactory


class STOMPClient(object):
    ACK_AUTO = "auto"
    ACK_CLIENT = "client"
    ACK_CLIENT_INDIVIDUAL = "client-individual"

    def __init__(self, host, port, login=None, passcode=None,
                 factory=None):
        self.shared_fabric = factory is not None
        self.host = host
        self.port = port
        self.login = login
        self.passcode = passcode
        self.factory = factory or SocketFactory()
        self.socket = None
        self.connected_event = threading.Event()
        self.s_id = 0
        self.callbacks = {}  # Subscription id -> callback
        self.destinations = {}  # destination -> (id, ack)

    def get_subscription_id(self):
        self.s_id += 1
        return str(self.s_id)

    def debug(self, message):
        logging.debug("STOMP(%s:%s): %s" % (
            self.host, self.port, message))

    def _connect(self):
        if not self.socket:
            self.debug("Connecting")
            self.socket = self.factory.connect_tcp(self.host, self.port,
                STOMPClientSocket)
            self.socket.set_client(self)
        self.connected_event.wait()

    def set_connected(self):
        self.debug("socket is connected")
        self.connected_event.set()

    def msg(self, command, headers, body=None):
        pass

    def start(self):
        self.debug("Starting client")
        if not self.shared_fabric:
            self.debug("Running client factory")
            threading.Thread(target=self.factory.run,
                name="stomp-factory", args=(True,)).start()

    def stop(self):
        if self.socket:
            self.socket.disconnect()

    def subscribe(self, destination, callback=None, ack=ACK_AUTO):
        self._connect()
        sid = self.get_subscription_id()
        self.debug("subscribe %s (id=%s)" % (destination, sid))
        self.callbacks[sid] = callback
        self.destinations[destination] = (sid, ack)
        self.socket.subscribe(destination, sid, ack)

    def unsubscribe(self, destination):
        self._connect()
        sid, _ = self.destinations[destination]
        self.debug("unsubscribe %s (id=%s)" % (destination, sid))
        self.socket.unsubscribe(sid)

    def send(self, message, destination):
        self._connect()
        self.debug("send (%s): %s" % (destination, message))
        self.socket.send_message(message, destination)

    def on_message(self, destination, sid, body):
        c = self.callbacks.get(sid)
        if c:
            c(destination, body)
