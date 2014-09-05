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
import re
## NOC modules
from noc.lib.nbsocket.socketfactory import SocketFactory
from protocols.line import LineProtocolSocket

logger = logging.getLogger(__name__)


class Sender(threading.Thread):
    rx_url = re.compile("^(?P<proto>\S+)://(?P<address>\S+):(?P<port>\d+)/?$")

    def __init__(self, daemon):
        self._daemon = daemon
        super(Sender, self).__init__(name="sender")
        self.factory = SocketFactory()
        self.channels = {}  # collector url -> Socket
        self.create_lock = threading.Lock()

    def run(self):
        logger.info("Running sender thread")
        self.factory.run(run_forever=True)

    def create_channel(self, url):
        with self.create_lock:
            c = self.channels.get(url)
            if c:
                return c
            logger.info("Creating channel %s", url)
            match = self.rx_url.match(url)
            proto, address, port = match.groups()
            c = getattr(self, "create_%s_channel" % proto)(
                url, address, int(port))
            self.channels[url] = c
            return c

    def feed(self, collector, metric, t, v):
        """
        Feed result to sender.
        :param collector: Collector url
        :param metric: metric name
        :param t: timestamp
        :param v: value
        """
        ch = self.channels.get(collector)
        if not ch:
            ch = self.create_channel(collector)
        logger.debug("sending %s %s %s %s", collector, metric, t, v)
        ch.feed(metric, t, v)

    def create_line_channel(self, url, address, port):
        return LineProtocolSocket(self, url, self.factory, address, port)

    def on_close(self, url):
        with self.create_lock:
            logging.info("Closing channel %s", url)
            if url in self.channels:
                del self.channels[url]
