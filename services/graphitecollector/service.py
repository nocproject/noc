#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Graphite Collector service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from optparse import make_option
import socket
from collections import defaultdict
import time
# Third-party modules
import tornado.ioloop
import tornado.gen
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter
from collector import GraphiteCollector


class GraphiteCollectorService(Service):
    name = "graphitecollector"

    #
    leader_group_name = "graphitecollector-%(dc)s-%(node)s"
    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    service_option_list = [
        make_option(
            "-l", "--listen",
            action="append", dest="listen",
            default=[os.environ.get("NOC_LISTEN", "0.0.0.0:2003")],
            help="Listen addresses"
        )
    ]

    def __init__(self):
        super(GraphiteCollectorService, self).__init__()
        self.metrics = []  # List of [metric, timestamp, value]
        self.pmwriter = None
        self.send_callback = None

    def on_activate(self):
        # Register RPC aliases
        self.pmwriter = self.open_rpc_global("pmwriter")
        # Listen sockets
        server = GraphiteCollector(self)
        for l in self.config.listen:
            if ":" in l:
                addr, port = l.split(":")
            else:
                addr, port = "", l
            self.logger.info("Starting graphite collector at %s:%s",
                             addr, port)
            try:
                server.listen(port, addr)
            except socket.error, why:
                self.logger.error(
                    "Failed to start graphite collector at %s:%s: %s",
                    addr, port, why
                )
        server.start()
        # Send spooled metrics every 250ms
        self.logger.debug("Stating metric sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_metrics,
            250,
            self.ioloop
        )
        self.send_callback.start()

    def spool_metric(self, metric, timestamp, value):
        self.metrics += [[metric, timestamp, value]]

    @tornado.gen.coroutine
    def send_metrics(self):
        """
        Periodic task to send collected messages to pmwriter
        """
        if self.metrics:
            yield self.pmwriter.metrics(self.metrics, _async=True)
            self.metrics = []

if __name__ == "__main__":
    GraphiteCollectorService().start()
