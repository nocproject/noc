# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Line protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket


class LineProtocolSocket(ConnectedTCPSocket):
    def __init__(self, sender, url, factory, address, port, local_address=None):
        self.sender = sender
        self.url = url
        self.feed_lock = Lock()
        super(LineProtocolSocket, self).__init__(factory, address,
                                                 port, local_address)

    def feed(self, metric, t, v):
        with self.feed_lock:
            self.write("%s %s %s\n" % (metric, v, t))

    def on_close(self):
        self.sender.on_close(self.url)

    def on_conn_refused(self):
        self.sender.on_close(self.url)
