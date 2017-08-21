#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import socket
from collections import defaultdict
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from trapserver import TrapServer


class TrapCollectorService(Service):
    name = "trapcollector"
    leader_group_name = "trapcollector-%(dc)s-%(node)s"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(TrapCollectorService, self).__init__()
        self.messages = []
        self.send_callback = None
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_map = {}
        self.invalid_sources = defaultdict(int)  # ip -> count
        self.omap = None
        self.fmwriter = None

    @tornado.gen.coroutine
    def on_activate(self):
        # Register RPC aliases
        self.omap = self.open_rpc("omap")
        self.fmwriter = self.open_rpc("fmwriter", pool=config.pool)
        # Listen sockets
        server = TrapServer(service=self)
        for l in config.trapcollector.listen.split(","):
            if ":" in l:
                addr, port = l.split(":")
            else:
                addr, port = "", l
            self.logger.info("Starting SNMP Trap server at %s:%s",
                             addr, port)
            try:
                server.listen(port, addr)
            except socket.error as e:
                self.logger.error(
                    "Failed to start SNMP Trap server at %s:%s: %s",
                    addr, port, e
                )
        server.start()
        # Send spooled messages every 250ms
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            250,
            self.ioloop
        )
        self.send_callback.start()
        # Get object mappings every 300s
        self.logger.debug("Stating object mapping task")
        self.mappings_callback = tornado.ioloop.PeriodicCallback(
            self.get_object_mappings,
            300000,
            self.ioloop
        )
        self.mappings_callback.start()
        self.ioloop.add_callback(self.get_object_mappings)
        # Report invalid sources every 60 seconds
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = tornado.ioloop.PeriodicCallback(
            self.report_invalid_sources,
            60000,
            self.ioloop
        )
        self.report_invalid_callback.start()

    def lookup_object(self, address):
        """
        Returns object id for given address or None when
        unknown source
        """
        obj_id = self.source_map.get(address)
        if not obj_id:
            # Register invalid event source
            if self.source_map:
                self.invalid_sources[address] += 1
            return None
        return obj_id

    def register_message(self, object, timestamp, data):
        """
        Spool message to be sent
        """
        self.perf_metrics["events_out"] += 1
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

    @tornado.gen.coroutine
    def get_object_mappings(self):
        """
        Periodic task to request object mappings
        """
        self.logger.debug("Requesting object mappings")
        sm = yield self.omap.get_trap_mappings(config.pool)
        if sm != self.source_map:
            self.logger.debug("Setting object mappings to: %s", sm)
            self.source_map = sm

    @tornado.gen.coroutine
    def report_invalid_sources(self):
        """
        Report invalid event sources
        """
        if not self.invalid_sources:
            return
        total = sum(self.invalid_sources[s] for s in self.invalid_sources)
        self.logger.info(
            "Dropping %d messages with invalid sources: %s",
            total,
            ", ".join("%s: %s" % (s, self.invalid_sources[s])
                      for s in self.invalid_sources)
        )
        self.invalid_sources = defaultdict(int)

    def on_object_map_change(self, topic):
        self.logger.info("Object mappings changed. Rerequesting")
        self.ioloop.add_callback(self.get_object_mappings)

if __name__ == "__main__":
    TrapCollectorService().start()
