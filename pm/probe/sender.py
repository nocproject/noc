# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
## NOC modules
from noc.lib.nbsocket.socketfactory import SocketFactory
from protocols.line import LineProtocolSocket
from protocols.pickle import PickleProtocolSocket

logger = logging.getLogger(__name__)


class Sender(threading.Thread):
    def __init__(self, daemon):
        self._daemon = daemon
        super(Sender, self).__init__(name="sender")
        self.factory = SocketFactory()
        self.channels = {}  # (proto, address, port) -> Socket
        self.create_lock = threading.Lock()

    def run(self):
        logger.info("Running sender thread")
        self.factory.run(run_forever=True)

    def create_channel(self, proto, address, port):
        with self.create_lock:
            c = self.channels.get((proto, address, port))
            if c:
                return c
            logger.info("Creating channel %s://%s:%s",
                        proto, address, port)
            c = getattr(self, "create_%s_channel" % proto)(
                address, int(port))
            self.channels[(proto, address, port)] = c
            return c

    def feed(self, policy, metric, t, v):
        """
        Feed result to sender.
        :param collector: FeedPolicy instance
        :param metric: metric name
        :param t: timestamp
        :param v: value
        """
        for c in policy.start():
            ch = self.channels.get(c)
            if not ch:
                ch = self.create_channel(*c)
            logger.debug("sending %s://%s:%s %s %s %s",
                         c[0], c[1], c[2], metric, t, v)
            ch.feed(metric, t, v)

    def create_line_channel(self, address, port):
        return LineProtocolSocket(self, self.factory, address, port)

    def create_pickle_channel(self, address, port):
        return PickleProtocolSocket(self, self.factory, address, port)

    def on_close(self, ch):
        with self.create_lock:
            logging.info("Closing channel %s://%s:%s", ch[0], ch[1], ch[2])
            if ch in self.channels:
                del self.channels[ch]
