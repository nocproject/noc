#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import socket
import datetime
from collections import defaultdict, namedtuple
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.service.base import Service
from noc.core.perf import metrics
from noc.services.syslogcollector.syslogserver import SyslogServer
from noc.services.syslogcollector.datastream import SysologDataStreamClient

SourceConfig = namedtuple("SourceConfig", ["id", "addresses", "bi_id", "process_events", "archive_events"])


class SyslogCollectorService(Service):
    name = "syslogcollector"
    leader_group_name = "syslogcollector-%(dc)s-%(node)s"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(SyslogCollectorService, self).__init__()
        self.messages = []
        self.send_callback = None
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_configs = {}  # id -> SourceConfig
        self.address_configs = {}  # address -> SourceConfig
        self.invalid_sources = defaultdict(int)  # ip -> count

    @tornado.gen.coroutine
    def on_activate(self):
        # Listen sockets
        server = SyslogServer(service=self)
        for l in config.syslogcollector.listen.split(","):
            if ":" in l:
                addr, port = l.split(":")
            else:
                addr, port = "", l
            self.logger.info("Starting syslog server at %s:%s",
                             addr, port)
            try:
                server.listen(port, addr)
            except socket.error as e:
                metrics["error", ("type", "socket_listen_error")] += 1
                self.logger.error(
                    "Failed to start syslog server at %s:%s: %s",
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
        # Report invalid sources every 60 seconds
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = tornado.ioloop.PeriodicCallback(
            self.report_invalid_sources,
            60000,
            self.ioloop
        )
        self.report_invalid_callback.start()
        # Start tracking changes
        self.ioloop.add_callback(self.get_object_mappings)

    def lookup_config(self, address):
        """
        Returns object id for given address or None when
        unknown source
        """
        cfg = self.address_configs.get(address)
        if not cfg:
            # Register invalid event source
            if self.address_configs:
                self.invalid_sources[address] += 1
            metrics["error", ("type", "object_not_found")] += 1
            return None
        return cfg

    def register_message(self, cfg, timestamp, message,
                         facility, severity):
        """
        Spool message to be sent
        """
        if cfg.process_events:
            # Send to classifier
            metrics["events_out"] += 1
            self.messages += [{
                "ts": timestamp,
                "object": cfg.id,
                "data": {
                    "source": "syslog",
                    "collector": config.pool,
                    "message": message
                }
            }]
        if cfg.archive_events and cfg.bi_id:
            # Archive message
            metrics["events_archived"] += 1
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            ts = now.strftime("%Y-%m-%d %H:%M:%S")
            msg = message.replace("\t", "\\t").replace("\n", "\\n")
            self.register_metrics(
                "syslog.date.ts.managed_object.facility.severity.message",
                [str("%s\t%s\t%s\t%d\t%d\t%s" % (date, ts, cfg.bi_id, facility, severity, msg))]
            )

    @tornado.gen.coroutine
    def send_messages(self):
        """
        Periodic task to send collected messages to classifier
        """
        if self.messages:
            messages, self.messages = self.messages, []
            self.mpub("events.%s" % config.pool, messages)

    @tornado.gen.coroutine
    def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = SysologDataStreamClient("cfgsyslog", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                yield client.query(
                    limit=config.syslogcollector.ds_limit,
                    filters=[
                        "pool(%s)" % config.pool
                    ],
                    block=1
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                yield tornado.gen.sleep(1)

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

    def update_source(self, data):
        # Get old config
        old_cfg = self.source_configs.get(data["id"])
        if old_cfg:
            old_addresses = set(old_cfg.addresses)
        else:
            old_addresses = set()
        # Build new config
        cfg = SourceConfig(
            data["id"],
            tuple(data["addresses"]),
            data.get("bi_id"),  # For backward compatibility
            data.get("process_events", True),  # For backward compatibility
            data.get("archive_events", False)
        )
        new_addresses = set(cfg.addresses)
        # Add new addresses, update remaining
        for addr in new_addresses:
            self.address_configs[addr] = cfg
        # Revoke stale addresses
        for addr in old_addresses - new_addresses:
            del self.address_configs[addr]
        # Update configs
        self.source_configs[data["id"]] = cfg
        # Update metrics
        metrics["sources_changed"] += 1

    def delete_source(self, id):
        cfg = self.source_configs.get(id)
        if not cfg:
            return
        for addr in cfg.addresses:
            del self.address_configs[addr]
        del self.source_configs[id]
        metrics["sources_deleted"] += 1


if __name__ == "__main__":
    SyslogCollectorService().start()
