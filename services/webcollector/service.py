#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Web Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.gen
import tornado.ioloop
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.services.webcollector.handlers.strizh import StrizhRequestHandler
from noc.core.perf import metrics


class WebCollectorService(Service):
    name = "webcollector"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(WebCollectorService, self).__init__()
        self.messages = []
        self.send_callback = None

    def get_handlers(self):
        r = []
        if config.webcollector.enable_strizh:
            r += [(
                r"^/api/webcollector/strizh/",
                StrizhRequestHandler,
                {"service": self}
            )]
        return r

    def on_activate(self):
        # Send spooled messages every 250ms
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            250,
            self.ioloop
        )
        self.send_callback.start()

    def register_message(self, object, timestamp, data):
        """
        Spool message to be sent
        """
        metrics["events_out"] += 1
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
            messages, self.messages = self.messages, []
            self.mpub("events.%s" % config.pool, messages)


if __name__ == "__main__":
    WebCollectorService().start()
