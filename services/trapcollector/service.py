#!./bin/python
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict, namedtuple
import asyncio

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.service.base import Service
from noc.services.trapcollector.trapserver import TrapServer
from noc.services.trapcollector.datastream import TrapDataStreamClient
from noc.core.ioloop.timers import PeriodicCallback

SourceConfig = namedtuple("SourceConfig", ["id", "addresses", "fm_pool"])


class TrapCollectorService(Service):
    name = "trapcollector"
    leader_group_name = "trapcollector-%(dc)s-%(node)s"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super().__init__()
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_configs = {}  # id -> SourceConfig
        self.address_configs = {}  # address -> SourceConfig
        self.invalid_sources = defaultdict(int)  # ip -> count

    async def on_activate(self):
        # Listen sockets
        server = TrapServer(service=self)
        for addr, port in server.iter_listen(config.trapcollector.listen):
            self.logger.info("Starting SNMP Trap server at %s:%s", addr, port)
            try:
                server.listen(port, addr)
            except OSError as e:
                metrics["error", ("type", "socket_listen_error")] += 1
                self.logger.error("Failed to start SNMP Trap server at %s:%s: %s", addr, port, e)
        server.start()
        # Report invalid sources every 60 seconds
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = PeriodicCallback(self.report_invalid_sources, 60000)
        self.report_invalid_callback.start()
        # Start tracking changes
        asyncio.get_running_loop().create_task(self.get_object_mappings())

    def lookup_config(self, address):
        """
        Returns object config for given address or None when
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

    def register_message(self, cfg, timestamp, data):
        """
        Spool message to be sent
        """
        metrics["events_out"] += 1
        self.pub("events.%s" % cfg.fm_pool, {"ts": timestamp, "object": cfg.id, "data": data})

    async def get_object_mappings(self):
        """
        Coroutine to request object mappings
        """
        self.logger.info("Starting to track object mappings")
        client = TrapDataStreamClient("cfgtrap", service=self)
        # Track stream changes
        while True:
            try:
                await client.query(
                    limit=config.trapcollector.ds_limit, filters=["pool(%s)" % config.pool], block=1
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                await asyncio.sleep(1)

    async def report_invalid_sources(self):
        """
        Report invalid event sources
        """
        if not self.invalid_sources:
            return
        total = sum(self.invalid_sources[s] for s in self.invalid_sources)
        self.logger.info(
            "Dropping %d messages with invalid sources: %s",
            total,
            ", ".join("%s: %s" % (s, self.invalid_sources[s]) for s in self.invalid_sources),
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
            data["id"], tuple(data["addresses"]), data.get("fm_pool", None) or config.pool,
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
    TrapCollectorService().start()
