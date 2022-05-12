#!./bin/python
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import asyncio
from collections import defaultdict
from dataclasses import asdict
from typing import Optional, Any, Dict

# Third-party modules
import orjson
import uuid

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.service.fastapi import FastAPIService
from noc.core.mx import (
    MX_STREAM,
    get_mx_partitions,
    MX_MESSAGE_TYPE,
    MX_SHARDING_KEY,
    MX_LABELS,
    MX_H_VALUE_SPLITTER,
)
from noc.core.service.stormprotection import storm_protection
from noc.services.trapcollector.trapserver import TrapServer
from noc.services.trapcollector.datastream import TrapDataStreamClient
from noc.services.trapcollector.sourceconfig import SourceConfig, ManagedObjectData
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.comp import smart_bytes


class TrapCollectorService(FastAPIService):
    name = "trapcollector"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super().__init__()
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_configs: Dict[str, SourceConfig] = {}  # id -> SourceConfig
        self.address_configs = {}  # address -> SourceConfig
        self.invalid_sources = defaultdict(int)  # ip -> count
        self.pool_partitions: Dict[str, int] = {}
        self.mx_message = config.message.enable_snmptrap

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
        storm_protection.initialize(
            config.trapcollector.storm_round_duration,
            config.trapcollector.storm_threshold_reduction,
            config.trapcollector.storm_record_ttl,
        )

    async def get_pool_partitions(self, pool: str) -> int:
        parts = self.pool_partitions.get(pool)
        if not parts:
            parts = await self.get_stream_partitions("events.%s" % pool)
            self.pool_partitions[pool] = parts
        return parts

    def lookup_config(self, address: str) -> Optional[SourceConfig]:
        """
        Returns object config for given address or None when
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
        self,
        cfg: SourceConfig,
        timestamp: int,
        data: Dict[str, Any],
        raw_data: Optional[bytes] = None,
        source_address: Optional[str] = None,
    ):
        """
        Spool message to be sent
        """
        metrics["events_out"] += 1
        self.publish(
            orjson.dumps(
                {
                    "ts": timestamp,
                    "object": cfg.id,
                    "data": data,
                }
            ),
            stream=cfg.stream,
            partition=cfg.partition,
        )
        if self.mx_message:
            metrics["events_message"] += 1
            n_partitions = get_mx_partitions()
            now = datetime.datetime.now()
            self.publish(
                value=orjson.dumps(
                    {
                        "timestamp": now.replace(microsecond=0),
                        "uuid": str(uuid.uuid4()),
                        "collector_type": "snmptrap",
                        "collector": config.pool,
                        "address": source_address,
                        "managed_object": asdict(cfg.managed_object),
                        "snmptrap": {"vars": raw_data},
                    }
                ),
                stream=MX_STREAM,
                partition=int(cfg.id) % n_partitions,
                headers={
                    MX_MESSAGE_TYPE: b"snmptrap",
                    MX_LABELS: smart_bytes(MX_H_VALUE_SPLITTER.join(cfg.effective_labels)),
                    MX_SHARDING_KEY: smart_bytes(cfg.id),
                },
            )

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
                    limit=config.trapcollector.ds_limit,
                    filters=[f"pool({config.pool})"],
                    block=True,
                    filter_policy="delete",
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
            bi_id=data.get("bi_id"),
            addresses=tuple(data["addresses"]),
            stream=f"events.{fm_pool}",
            partition=int(data["id"]) % num_partitions,
            effective_labels=data.get("effective_labels", []),
            storm_policy=data["storm_policy"],
            storm_threshold=data["storm_threshold"],
        )
        if config.message.enable_snmptrap and "managed_object" in data:
            cfg.managed_object = ManagedObjectData(**data["managed_object"])
        new_addresses = set(cfg.addresses)
        # Add new addresses, update remaining
        for addr in new_addresses:
            self.address_configs[addr] = cfg
        # Revoke stale addresses
        for addr in old_addresses - new_addresses:
            if addr in self.address_configs:
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
    TrapCollectorService().start()
