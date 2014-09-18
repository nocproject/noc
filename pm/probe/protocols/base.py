# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base socket mixin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
## NOC modules
from noc.lib.log import PrefixLoggerAdapter


class SenderSocket(object):
    name = None

    def __init__(self, sender, logger, address, port):
        self.sender = sender
        self.ch = (self.name, address, port)
        self.feed_lock = Lock()
        self.data = []
        self.logger = PrefixLoggerAdapter(
            logger, "%s://%s:%s" % (self.name, address, port))

    def feed(self, metric, t, v):
        """
        Feed metric to channel.
        Sending delayed until flush() called
        """
        with self.feed_lock:
            self.logger.debug("Feeding %s %s %s", metric, t, v)
            self.data += [(metric, v, t)]

    def flush(self):
        raise NotImplementedError()

    def on_close(self):
        self.sender.on_close(self.ch)

    def on_conn_refused(self):
        self.sender.on_close(self.ch)
