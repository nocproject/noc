#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Node Manager service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from optparse import make_option
import socket
# Third-party modules
import tornado.ioloop
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter
from syslogserver import SyslogServer


class FMWriterService(Service):
    name = "syslogcollector"

    #
    leader_group_name = "syslogcollector-%(env)s-%(dc)s-%(node)s"
    pooled = True
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
            default=[os.environ.get("NOC_LISTEN", "0.0.0.0:514")],
            help="Listen addresses"
        )
    ]

    def __init__(self):
        super(FMWriterService, self).__init__()
        self.messages = []
        self.send_callback = None

    def on_activate(self):
        # Register RPC aliases
        self.rpc.alias("fmwriter", "fmwriter", self.config.pool)
        # Listen sockets
        server = SyslogServer(service=self)
        for l in self.config.listen:
            if ":" in l:
                addr, port = l.split(":")
            else:
                addr, port = "", l
            self.logger.info("Starting syslog server at %s:%s",
                             addr, port)
            try:
                server.listen(port, addr)
            except socket.error, why:
                self.logger.error(
                    "Failed to start syslog server at %s:%s: %s",
                    addr, port, why
                )
        server.start()
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            250,
            self.ioloop
        )
        self.send_callback.start()

    def lookup_object(self, address):
        """
        Returns object id for given address or None when
        unknown source
        """
        return 1

    def register_message(self, object, timestamp, message,
                         facility, severity):
        """
        Spool message to be sent
        """
        self.messages += [{
            "ts": timestamp,
            "object": object,
            "data": {
            "source": "syslog",
                "collector": "???",
                "message": message
            }
        }]
        # self.rpc.fmwriter.event(timestamp, object, {
        #    "source": "syslog",
        #    "collector": "???",
        #    "message": message
        #})

    def send_messages(self):
        self.rpc.fmwriter.events(self.messages)
        self.messages = []


if __name__ == "__main__":
    FMWriterService().start()
