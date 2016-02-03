#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen
import threading
## NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.scheduler = None
        self.send_callback = None
        self.messages = []
        self.messages_lock = threading.Lock()
        self.fmwriter = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.fmwriter = self.open_rpc("fmwriter", pool=self.config.pool)
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            250,
            self.ioloop
        )
        self.send_callback.start()
        #
        self.scheduler = Scheduler(
            "discovery",
            pool=self.config.pool,
            reset_running=True,
            max_threads=self.config.max_threads,
            ioloop=self.ioloop
        )
        self.scheduler.service = self
        self.scheduler.run()

    def register_message(self, object, timestamp, data):
        """
        Spool message to be sent
        """
        with self.messages_lock:
            self.messages += [{
                "ts": timestamp,
                "object": object,
                "data": data
            }]

    @tornado.gen.coroutine
    def send_messages(self):
        """
        Periodic task to send collected messages to fmwriter
        """
        if self.messages:
            with self.messages_lock:
                msg = self.messages
                self.messages = []
            yield self.fmwriter.events(msg, _notify=True)


if __name__ == "__main__":
    DiscoveryService().start()
