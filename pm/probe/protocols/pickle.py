# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pickle protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
from cPickle import dumps
import struct
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket


class PickleProtocolSocket(ConnectedTCPSocket):
    def __init__(self, sender, factory, address, port, local_address=None):
        self.sender = sender
        self.ch = ("pickle", address, port)
        self.feed_lock = Lock()
        super(PickleProtocolSocket, self).__init__(factory, address,
                                                 port, local_address)

    def feed(self, metric, t, v):
        p = [(metric, (t, v))]
        payload = dumps(p, protocol=2)
        header = struct.pack("!L", len(payload))
        with self.feed_lock:
            self.write(header + payload)

    def on_close(self):
        self.sender.on_close(self.ch)

    def on_conn_refused(self):
        self.sender.on_close(self.ch)
