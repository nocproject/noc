#!./bin/python
# ---------------------------------------------------------------------
# Syslog Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import asyncio
import uuid
from collections import defaultdict
from dataclasses import asdict
from typing import Optional, Dict, Any

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.service.fastapi import FastAPIService
from noc.core.perf import metrics
from noc.core.mx import (
    MX_STREAM,
    MessageType,
    get_mx_partitions,
    MX_MESSAGE_TYPE,
    MX_SHARDING_KEY,
    MX_LABELS,
    MX_H_VALUE_SPLITTER,
)
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.fm.enum import EventSource, SyslogSeverity
from noc.core.service.stormprotection import StormProtection
from noc.services.syslogcollector.syslogserver import SyslogServer
from noc.services.syslogcollector.datastream import SysologDataStreamClient
from noc.services.syslogcollector.sourceconfig import SourceConfig, ManagedObjectData
from noc.core.comp import DEFAULT_ENCODING

SYSLOGCOLLECTOR_STORM_ALARM_CLASS = "NOC | Managed Object | Storm Control"


class SyslogCollectorService(FastAPIService):
    name = "syslogcollector"
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
        self.storm_protection: Optional[StormProtection] = None

    async def on_activate(self):
        # Listen sockets
        server = SyslogServer(service=self)
        for addr, port in server.iter_listen(config.syslogcollector.listen):
            self.logger.info("Starting syslog server at %s:%s", addr, port)
            try:
                await server.listen(port, addr)
            except OSError as e:
                metrics["error", ("type", "socket_listen_error")] += 1
                self.logger.error("Failed to start syslog server at %s:%s: %s", addr, port, e)
        server.start()
        # Report invalid sources every 60 seconds
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = PeriodicCallback(self.report_invalid_sources, 60000)
        self.report_invalid_callback.start()
        self.storm_protection = StormProtection(
            config.syslogcollector.storm_round_duration,
            config.syslogcollector.storm_threshold_reduction,
            config.syslogcollector.storm_record_ttl,
            SYSLOGCOLLECTOR_STORM_ALARM_CLASS,
        )
        self.storm_protection.initialize()
        self.storm_protection.raise_alarm_handler = self.on_storm_raise_alarm
        self.storm_protection.close_alarm_handler = self.on_storm_close_alarm
        # Start tracking changes
        asyncio.get_running_loop().create_task(self.get_object_mappings())

    def on_storm_raise_alarm(self, ip_address):
        cfg = self.address_configs[ip_address]
        msg = {
            "$op": "raise",
            "managed_object": cfg.id,
            "alarm_class": SYSLOGCOLLECTOR_STORM_ALARM_CLASS,
            "vars": {"collector": self.name},
        }
        self._publish_message(cfg, msg)

    def on_storm_close_alarm(self, ip_address):
        cfg = self.address_configs[ip_address]
        msg = {"$op": "clear"}
        self._publish_message(cfg, msg)

    def _publish_message(self, cfg, msg: Dict[str, Any]):
        msg["timestamp"] = datetime.datetime.now().isoformat()
        msg["reference"] = f"{SYSLOGCOLLECTOR_STORM_ALARM_CLASS}{cfg.id}"
        self.publish(orjson.dumps(msg), stream=f"dispose.{config.pool}", partition=cfg.partition)

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

    def register_syslog_message(
        self,
        cfg: SourceConfig,
        timestamp: int,
        message: str,
        facility: int,
        severity: int,
        source_address: str = None,
    ) -> None:
        """
        Spool message to be sent
        """
        if cfg.storm_policy != "D" and severity >= config.syslogcollector.storm_min_severity:
            need_block = self.storm_protection.process_message(source_address, cfg)
            if need_block:
                return
        message_id = None
        if config.fm.generate_message_id:
            message_id = str(uuid.uuid4())
        if cfg.process_events:
            # Send to classifier
            metrics["events_out"] += 1
            self.publish(
                orjson.dumps(
                    {
                        "ts": timestamp,
                        "target": {
                            "address": source_address,
                            "name": cfg.name or "",
                            "pool": config.pool,
                            "profile": cfg.sa_profile or "",
                            "id": cfg.id,
                        },
                        "type": {
                            "source": EventSource.SYSLOG.value,
                            "facility": facility,
                            "severity": SyslogSeverity(severity).noc_severity.value,
                        },
                        "message": message,
                        "data": [
                            {"name": "facility", "value": str(facility)},
                            {"name": "severity", "value": str(severity)},
                            {"name": "message_id", "value": message_id or ""},
                        ],
                    }
                ),
                stream=cfg.stream,
                partition=cfg.partition,
            )
        now = datetime.datetime.now().replace(microsecond=0)
        if cfg.archive_events and cfg.bi_id:
            # Archive message
            metrics["events_archived"] += 1
            self.register_metrics(
                "syslog",
                [
                    {
                        "date": now.date().isoformat(),
                        "ts": now.isoformat(sep=" "),
                        "managed_object": cfg.bi_id,
                        "facility": facility,
                        "severity": severity,
                        "message": message,
                    }
                ],
            )
        if config.message.enable_syslog and not cfg.managed_object:
            self.logger.warning(
                "[%s] Cfg source not ManagedObject Meta."
                " Please Reboot cfgtarget datastream and reboot collector. Skipping..",
                source_address,
            )
            return
        elif config.message.enable_syslog:
            metrics["events_message"] += 1
            n_partitions = get_mx_partitions()
            self.publish(
                value=orjson.dumps(
                    {
                        "timestamp": datetime.datetime.fromtimestamp(timestamp).replace(
                            microsecond=0
                        ),
                        "message_id": message_id,
                        "collector_type": "syslog",
                        "collector": config.pool,
                        "address": source_address,
                        "managed_object": asdict(cfg.managed_object),
                        "data": {
                            "facility": facility,
                            "severity": severity,
                            "message": message,
                        },
                    }
                ),
                stream=MX_STREAM,
                partition=int(cfg.id) % n_partitions,
                headers={
                    MX_MESSAGE_TYPE: MessageType.SYSLOG.value.encode(),
                    MX_LABELS: MX_H_VALUE_SPLITTER.join(cfg.effective_labels).encode(
                        DEFAULT_ENCODING
                    ),
                    MX_SHARDING_KEY: str(cfg.id).encode(DEFAULT_ENCODING),
                },
            )

    async def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = SysologDataStreamClient("cfgtarget", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                await client.query(
                    limit=config.syslogcollector.ds_limit,
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
        cfg_syslog = data.pop("syslog", None)
        # Get pool and sharding information
        fm_pool = data.get("fm_pool", None) or config.pool
        num_partitions = await self.get_pool_partitions(fm_pool)
        # Build new config
        cfg = SourceConfig(
            id=data["id"],
            addresses=tuple([a["address"] for a in data["addresses"] if a["syslog_source"]]),
            bi_id=data.get("bi_id"),  # For backward compatibility
            process_events=data.get("process_events", True),  # For backward compatibility
            archive_events=cfg_syslog.get("archive_events", False) if cfg_syslog else False,
            stream=f"events.{fm_pool}",
            sa_profile=data.get("sa_profile"),
            partition=int(data["id"]) % num_partitions,
            effective_labels=data.get("effective_labels", []),
        )
        if not cfg_syslog or not cfg.addresses:
            await self.delete_source(data["id"])
            return
        if config.message.enable_syslog and "opaque_data" in data:
            cfg.managed_object = ManagedObjectData(**data["opaque_data"])
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
    SyslogCollectorService().start()
