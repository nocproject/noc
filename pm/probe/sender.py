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
from protocols.udp import UDPProtocolSocket

logger = logging.getLogger(__name__)


class Sender(threading.Thread):
    def __init__(self, daemon):
        self._daemon = daemon
        super(Sender, self).__init__(name="sender")
        self.factory = SocketFactory()
        self.channels = {}  # (proto, address, port) -> Socket
        self.create_lock = threading.Lock()
        self.feed_lock = threading.Lock()
        self.ready_channels = set()

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
        with self.feed_lock:
            for c in policy.start():
                ch = self.channels.get(c)
                if not ch:
                    ch = self.create_channel(*c)
                ch.feed(metric, t, v)
                self.ready_channels.add(ch)

    def flush(self):
        """
        Flush data from sender channels
        """
        with self.feed_lock:
            if self.ready_channels:
                logger.debug("Flushing channels %d channels",
                             len(self.ready_channels))
                for ch in self.ready_channels:
                    ch.flush()
                self.ready_channels = set()

    def create_line_channel(self, address, port):
        return LineProtocolSocket(self, self.factory, address, port)

    def create_pickle_channel(self, address, port):
        return PickleProtocolSocket(self, self.factory, address, port)

    def create_udp_channel(self, address, port):
        return UDPProtocolSocket(self, self.factory, address, port)

    def on_close(self, ch):
        with self.create_lock:
            logging.info("Closing channel %s://%s:%s", ch[0], ch[1], ch[2])
            if ch in self.channels:
                del self.channels[ch]
