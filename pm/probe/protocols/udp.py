# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UDP protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
## NOC modules
from noc.lib.nbsocket.udpsocket import UDPSocket


class UDPProtocolSocket(UDPSocket):
    def __init__(self, sender, factory, address, port, local_address=None):
        self.sender = sender
        self.address = address
        self.port = port
        self.local_address = local_address
        self.ch = ("udp", address, port)
        self.feed_lock = Lock()
        super(UDPProtocolSocket, self).__init__(factory)

    def feed(self, metric, t, v):
        with self.feed_lock:
            self.sendto(
                "%s %s %s\n" % (metric, v, t),
                (self.address, self.port)
            )

    def on_close(self):
        self.sender.on_close(self.ch)

    def on_conn_refused(self):
        self.sender.on_close(self.ch)
