#!./bin/python
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
import asyncio
from typing import Optional, Dict

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.service.tornado import TornadoService
from noc.core.perf import metrics
from noc.services.syslogcollector.syslogserver import SyslogServer
from noc.services.syslogcollector.datastream import SysologDataStreamClient
from noc.services.syslogcollector.sourceconfig import SourceConfig
from noc.core.ioloop.timers import PeriodicCallback


class SyslogCollectorService(TornadoService):
    name = "syslogcollector"
    leader_group_name = "syslogcollector-%(dc)s-%(node)s"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super().__init__()
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_configs = {}  # id -> SourceConfig
        self.address_configs = {}  # address -> SourceConfig
        self.invalid_sources = defaultdict(int)  # ip -> count
        self.pool_partitions: Dict[str, int] = {}

    async def on_activate(self):
        # Listen sockets
        server = SyslogServer(service=self)
        for addr, port in server.iter_listen(config.syslogcollector.listen):
            self.logger.info("Starting syslog server at %s:%s", addr, port)
            try:
                server.listen(port, addr)
            except OSError as e:
                metrics["error", ("type", "socket_listen_error")] += 1
                self.logger.error("Failed to start syslog server at %s:%s: %s", addr, port, e)
        server.start()
        # Report invalid sources every 60 seconds
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = PeriodicCallback(self.report_invalid_sources, 60000)
        self.report_invalid_callback.start()
        # Start tracking changes
        asyncio.get_running_loop().create_task(self.get_object_mappings())

    async def get_pool_partitions(self, pool: str) -> int:
        parts = self.pool_partitions.get(pool)
        if not parts:
            parts = await self.get_stream_partitions("events.%s" % pool)
            self.pool_partitions[pool] = parts
        return parts

    def lookup_config(self, address: str) -> Optional[SourceConfig]:
        """
        Returns object id for given address or None when
        unknown source
        """
        cfg = self.address_configs.get(address)
        if cfg:
            return cfg
        # Register invalid event source
        if self.address_configs:
            self.invalid_sources[address] += 1
        metrics["error", ("type", "object_not_found")] += 1
        return None

    def register_message(
        self, cfg: SourceConfig, timestamp: int, message: str, facility: int, severity: int
    ) -> None:
        """
        Spool message to be sent
        """
        if cfg.process_events:
            # Send to classifier
            metrics["events_out"] += 1
            self.publish(
                orjson.dumps(
                    {
                        "ts": timestamp,
                        "object": cfg.id,
                        "data": {"source": "syslog", "collector": config.pool, "message": message},
                    }
                ),
                stream=cfg.stream,
                partition=cfg.partition,
            )
        if cfg.archive_events and cfg.bi_id:
            # Archive message
            metrics["events_archived"] += 1
            now = datetime.datetime.now()
            ts = now.strftime("%Y-%m-%d %H:%M:%S")
            date = ts.split(" ")[0]
            self.register_metrics(
                "syslog",
                [
                    {
                        "date": date,
                        "ts": ts,
                        "managed_object": cfg.bi_id,
                        "facility": facility,
                        "severity": severity,
                        "message": message,
                    }
                ],
            )

    async def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = SysologDataStreamClient("cfgsyslog", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                await client.query(
                    limit=config.syslogcollector.ds_limit,
                    filters=["pool(%s)" % config.pool],
                    block=1,
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

    async def update_source(self, data):
        # Get old config
        old_cfg = self.source_configs.get(data["id"])
        if old_cfg:
            old_addresses = set(old_cfg.addresses)
        else:
            old_addresses = set()
        # Get pool and sharding information
        fm_pool = data.get("fm_pool", None) or config.pool
        num_partitions = await self.get_pool_partitions(fm_pool)
        # Build new config
        cfg = SourceConfig(
            id=data["id"],
            addresses=tuple(data["addresses"]),
            bi_id=data.get("bi_id"),  # For backward compatibility
            process_events=data.get("process_events", True),  # For backward compatibility
            archive_events=data.get("archive_events", False),
            stream="events.%s" % fm_pool,
            partition=int(data["id"]) % num_partitions,
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

    async def delete_source(self, id):
        cfg = self.source_configs.get(id)
        if not cfg:
            return
        for addr in cfg.addresses:
            del self.address_configs[addr]
        del self.source_configs[id]
        metrics["sources_deleted"] += 1


if __name__ == "__main__":
    SyslogCollectorService().start()
