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
from typing import Optional, Any, Dict, List, Tuple
import base64

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.service.fastapi import FastAPIService
from noc.core.fm.enum import EventSource
from noc.core.mx import (
    MX_STREAM,
    get_mx_partitions,
    MessageType,
    MX_MESSAGE_TYPE,
    MX_SHARDING_KEY,
    MX_LABELS,
    MX_H_VALUE_SPLITTER,
)
from noc.core.service.stormprotection import StormProtection
from noc.services.trapcollector.trapserver import TrapServer
from noc.services.trapcollector.datastream import TrapDataStreamClient
from noc.services.trapcollector.sourceconfig import SourceConfig, ManagedObjectData
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.comp import smart_bytes

TRAPCOLLECTOR_STORM_ALARM_CLASS = "NOC | Managed Object | Storm Control | SNMP"
SNMP_TRAP_OID = "1.3.6.1.6.3.1.1.4.1.0"


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
        self.storm_protection: Optional[StormProtection] = None

    async def on_activate(self):
        # Listen sockets
        server = TrapServer(service=self)
        for addr, port in server.iter_listen(config.trapcollector.listen):
            self.logger.info("Starting SNMP Trap server at %s:%s", addr, port)
            try:
                await server.listen(port, addr)
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
        self.storm_protection = StormProtection(
            config.trapcollector.storm_round_duration,
            config.trapcollector.storm_threshold_reduction,
            config.trapcollector.storm_record_ttl,
            TRAPCOLLECTOR_STORM_ALARM_CLASS,
        )
        self.storm_protection.initialize()
        self.storm_protection.raise_alarm_handler = self.on_storm_raise_alarm
        self.storm_protection.close_alarm_handler = self.on_storm_close_alarm

    def on_storm_raise_alarm(self, ip_address):
        cfg = self.address_configs[ip_address]
        msg = {
            "$op": "raise",
            "managed_object": cfg.id,
            "alarm_class": TRAPCOLLECTOR_STORM_ALARM_CLASS,
        }
        self._publish_message(cfg, msg)

    def on_storm_close_alarm(self, ip_address):
        cfg = self.address_configs[ip_address]
        msg = {"$op": "clear"}
        self._publish_message(cfg, msg)

    def _publish_message(self, cfg, msg: Dict[str, Any]):
        msg["timestamp"] = datetime.datetime.now().isoformat()
        msg["reference"] = f"{TRAPCOLLECTOR_STORM_ALARM_CLASS}{cfg.id}"
        self.publish(orjson.dumps(msg), stream=f"dispose.{config.pool}", partition=cfg.partition)

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

    def register_trap_message(
        self, cfg: SourceConfig, timestamp: int, data: Dict[str, Any], address: str = None
    ):
        """
        Spool message to be sent
        """
        metrics["events_out"] += 1
        self.publish(
            orjson.dumps(
                {
                    "ts": timestamp,
                    "target": {
                        "address": address,
                        "name": cfg.name or "",
                        "pool": config.pool,
                        "id": cfg.id,
                    },
                    "type": {"source": EventSource.SNMP_TRAP.value, "id": data.get(SNMP_TRAP_OID)},
                    "data": [{"name": k, "value": v, "snmp_raw": True} for k, v in data.items()],
                    # + [{"name": "message_id", "value": message_id}]
                }
            ),
            stream=cfg.stream,
            partition=cfg.partition,
        )

    def register_mx_message(
        self,
        cfg: SourceConfig,
        timestamp: int,
        source_address: Optional[str] = None,
        message_id: Optional[str] = None,
        raw_pdu: Optional[bytes] = None,
        raw_varbinds: List[Tuple[str, Any, bytes]] = None,
    ):
        metrics["events_mx_message"] += 1
        if not cfg.managed_object:
            self.logger.warning(
                "[%s] Cfg source not ManagedObject Meta."
                " Please Reboot cfgtrap datastream and reboot collector. Skipping..",
                source_address,
            )
            return
        n_partitions = get_mx_partitions()
        self.publish(
            value=orjson.dumps(
                {
                    "timestamp": datetime.datetime.fromtimestamp(timestamp).replace(microsecond=0),
                    "message_id": message_id,
                    "collector_type": "snmptrap",
                    "collector": config.pool,
                    "address": source_address,
                    "managed_object": asdict(cfg.managed_object),
                    "data": {
                        "vars": [
                            {
                                "oid": oid,
                                "value": value,
                                "value_raw": base64.b64encode(value_raw).decode("utf-8"),
                            }
                            for oid, value, value_raw in raw_varbinds
                        ],
                        "raw_pdu": base64.b64encode(raw_pdu).decode("utf-8"),
                    },
                }
            ),
            stream=MX_STREAM,
            partition=int(cfg.id) % n_partitions,
            headers={
                MX_MESSAGE_TYPE: MessageType.SNMPTRAP.value.encode(),
                MX_LABELS: smart_bytes(MX_H_VALUE_SPLITTER.join(cfg.effective_labels)),
                MX_SHARDING_KEY: str(cfg.id).encode(),
            },
        )

    async def get_object_mappings(self):
        """
        Coroutine to request object mappings
        """
        self.logger.info("Starting to track object mappings")
        client = TrapDataStreamClient("cfgtarget", service=self)
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
        cfg_trap = data.pop("trap", None)
        # Get pool and sharding information
        fm_pool = data.get("fm_pool", None) or config.pool
        num_partitions = await self.get_pool_partitions(fm_pool)
        # Build new config
        cfg = SourceConfig(
            id=data["id"],
            name=data["name"],
            bi_id=data.get("bi_id"),
            addresses=tuple([a["address"] for a in data["addresses"] if a["trap_source"]]),
            stream=f"events.{fm_pool}",
            partition=int(data["id"]) % num_partitions,
            effective_labels=data.get("effective_labels", []),
        )
        if not cfg_trap or not cfg.addresses:
            await self.delete_source(data["id"])
            return
        if config.message.enable_snmptrap and "opaque_data" in data:
            cfg.managed_object = ManagedObjectData(**data["opaque_data"])
        if "storm_policy" in cfg_trap:
            cfg.storm_policy = cfg_trap["storm_policy"]
            cfg.storm_threshold = cfg_trap["storm_threshold"]
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
