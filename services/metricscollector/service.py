#!./bin/python
# ----------------------------------------------------------------------
# metricscollector service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import operator
import re
import datetime
from time import perf_counter
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List, Dict, Set, Iterable, DefaultDict, FrozenSet
from collections import defaultdict

# Third-party modules
import cachetools

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.perf import metrics
from noc.core.service.fastapi import FastAPIService
from noc.core.jsonutils import iter_chunks
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.nodatachecker import NoDataChecker
from noc.core.mx import MessageType, MX_FROM_COLLECTOR
from noc.services.metricscollector.datastream import MetricsDataStreamClient, SourceStreamClient
from noc.services.metricscollector.sourceconfig import (
    SourceConfig,
    RemoteSystemConfig,
    SensorConfig,
)
from noc.services.metricscollector.models.channel import RemoteSystemChannel

NS = 1_000_000_000


@dataclass(frozen=True)
class CfgItem(object):
    id: str
    ch_table: str
    ch_field: str
    collector: str
    coll_field: str
    allow_partial_match: bool
    labels: FrozenSet[str]
    aliases: List[str]
    unit: str
    preference: int

    @classmethod
    def from_data(cls, rid, table, field, data) -> "CfgItem":
        return CfgItem(
            id=rid,
            ch_table=table,
            ch_field=field,
            collector=data["collector"],
            coll_field=data["field"],
            allow_partial_match=bool(data.get("allow_partial_match")),
            labels=frozenset(data["labels"] or []),
            aliases=data["aliases"],
            unit=data.get("unit"),
            preference=data["preference"],
        )


class MetricsCollectorService(FastAPIService):
    name = "metricscollector"
    # use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/metricscollector`)"
    # Cache regex for partial match
    _rx_name_cache = cachetools.LRUCache(1000)
    _rs_key_cache = cachetools.TTLCache(10, ttl=120)

    def __init__(self):
        super().__init__()
        self.mappings: DefaultDict[Tuple[str, str], List[CfgItem]] = defaultdict(list)
        self.rx_mappings: DefaultDict[Tuple[str, re.Pattern], List[CfgItem]] = defaultdict(list)
        self.id_mappings: Dict[str, List[CfgItem]] = {}
        self.n_parts: int = 0
        self.add_sources = 0
        self.ready_event: Optional[asyncio.Event] = asyncio.Event()
        self.event_source_ready = asyncio.Event()
        self.no_data_checker = NoDataChecker(
            nodata_record_ttl=config.metricscollector.nodata_record_ttl,
            nodata_round_duration=config.metricscollector.nodata_round_duration,
            collector="metricscollector",
        )
        # Source Configs: ManagedObject & Agent
        self.source_configs: Dict[str, SourceConfig] = {}  # id -> SourceConfig
        self.source_map: Dict[str, str] = {}
        self.channels: Dict[str, RemoteSystemChannel] = {}
        # Remote Systems Config
        self.banned_rs = set()
        self.remote_system_config: Dict[str, RemoteSystemConfig] = {}
        self.remote_system_map: Dict[str, str] = {}
        # Sensors
        self.sensor_configs: Dict[str, SensorConfig] = {}
        self.stopping = False
        # Queue of channels to flush
        self.flush_queue: asyncio.Queue[RemoteSystemChannel] = asyncio.Queue()
        if config.metricscollector.listen:
            address, port = config.metricscollector.listen.split(":")
            if address == "auto":
                address = config.node
            self.address, self.port = address, int(port)

    def get_channel(
        self, remote_system: RemoteSystemConfig, collector: str, batch_delay: Optional[int] = None
    ) -> Optional["RemoteSystemChannel"]:
        """
        Create channel for received data
            remote_system: External System for channel
            collector: Collector name
            batch_delay: Send data delay (in second)
        """
        # Unknown channel
        # Unauthorized channels
        if remote_system.name not in self.channels:
            self.channels[remote_system.name] = RemoteSystemChannel(
                self,
                remote_system,
                collector,
                batch_delay=batch_delay,
                logger=self.logger,
            )
        return self.channels.get(remote_system.name)

    async def flush_data(self):
        """Flush data"""
        while not self.stopping:
            ch = await self.flush_queue.get()
            n_records = ch.records
            self.logger.info("[%s] Flush Records: %s", ch.remote_system.name, n_records)
            parts = defaultdict(list)
            for (clock, target, labels), mms in ch.data.items():
                try:
                    target = self.source_configs[target]
                except KeyError:
                    continue
                if not target.managed_object:
                    continue
                ts = datetime.datetime.fromtimestamp(clock)
                out = {}
                for metric, value in mms.items():
                    try:
                        cfg = self.id_mappings[metric][0]
                    except KeyError:
                        continue
                    if cfg.ch_table not in out:
                        out[cfg.ch_table] = {
                            "ts": (ts.timestamp() + config.tz_utc_offset) * NS,
                            "scope": cfg.ch_table,
                            "labels": list(labels),
                            # "service": item.service,
                            "managed_object": target.managed_object,
                            "remote_system": ch.remote_system.bi_id,
                            "_units": {},
                        }
                    out[cfg.ch_table][cfg.ch_field] = value
                    out[cfg.ch_table]["_units"][cfg.ch_field] = cfg.unit or "1"
                parts[target.bi_id % self.n_parts] += list(out.values())
            # Sensors
            for (clock, cfg_id), value in ch.sensors_data.items():
                try:
                    cfg = self.sensor_configs[cfg_id]
                except KeyError:
                    continue
                ts = datetime.datetime.fromtimestamp(clock)
                parts[cfg.bi_id % self.n_parts].append(
                    {
                        "ts": (ts.timestamp() + config.tz_utc_offset) * NS,
                        "scope": "sensor",
                        "labels": [f"noc::sensor::{cfg.name}"],
                        "sensor": cfg.bi_id,
                        "managed_object": cfg.managed_object,
                        "_units": {"value_delta": cfg.units, "value": cfg.units},
                        "remote_system": ch.remote_system.bi_id,
                        "value": value,
                        "value_delta": value,
                    }
                )
            # Unfreeze channel
            self.logger.info("Send Records To Stream")
            for partition, items in parts.items():
                await self.send_records(items, partition)
                await asyncio.sleep(1)
            del parts
            ch.flush_complete()

    async def send_records(self, data: List[Any], partition: Optional[int] = None):
        """Send data to"""
        for d in iter_chunks(
            data,
            max_size=config.metricscollector.batch_max_message_size,
        ):
            self.publish(
                value=d,
                stream="metrics",
                partition=partition,  # self.object.bi_id % metrics_svc_slots,
                headers={},
            )

    async def report_invalid_sources(self):
        """Report invalid event sources"""
        for ch in self.channels:
            ch = self.channels[ch]
            self.logger.info(
                "[%s] Processed controlled hosts: %s",
                ch.remote_system.name,
                len(ch.last_received_hosts),
            )
            for target_id, clock in ch.last_received_hosts.items():
                try:
                    target = self.source_configs[target_id]
                except KeyError:
                    continue
                ts = datetime.datetime.fromtimestamp(clock)
                self.no_data_checker.register_data(
                    str(target.bi_id),
                    ts=ts,
                    collector=ch.collector,
                    remote_system=ch.remote_system.name,
                )
            if ch.unknown_hosts:
                self.logger.info(
                    "[%s] Unknown Hosts: %s", ch.remote_system.name, ",".join(ch.unknown_hosts)
                )
                await self.send_message(
                    {
                        "collector": ch.collector,
                        "remote_system": ch.remote_system.name,
                        "hosts": list(ch.unknown_hosts),
                    },
                    MessageType.UNKNOWN_TARGET,
                    headers={MX_FROM_COLLECTOR: ch.collector.encode()},
                )
            if ch.unknown_metrics:
                self.logger.info(
                    "[%s] Unknown Metrics: %s", ch.remote_system.name, ",".join(ch.unknown_metrics)
                )

    async def init_api(self):
        # Postpone initialization process until config datastream is fully processed
        self.n_parts = await self.get_stream_partitions("metrics")
        asyncio.get_running_loop().create_task(self.get_metrics_mappings())
        # Set by datastream.on_ready
        await self.ready_event.wait()
        if config.datastream.enable_cfgtarget:
            asyncio.get_running_loop().create_task(self.get_object_mappings())
            await self.event_source_ready.wait()
        self.logger.info("Stating invalid sources reporting task")
        self.report_invalid_callback = PeriodicCallback(self.report_invalid_sources, 120000)
        self.report_invalid_callback.start()
        if config.metricscollector.nodata_round_duration:
            self.no_data_checker.initialize()
        # For used MX service
        self.mx_partitions = await self.get_stream_partitions("message") or 0
        # Process as usual
        await super().init_api()

    async def on_activate(self):
        check_callback = PeriodicCallback(
            self.check_channels, config.metricscollector.batch_delay_s
        )
        check_callback.start()
        asyncio.create_task(self.flush_data())

    async def check_channels(self):
        ts = perf_counter()
        expired = [c for c in self.channels.values() if c.is_expired(ts)]
        for ch in expired:
            self.logger.debug("[%s] Flushing due to timeout", ch.remote_system)
            await ch.schedule_flush()

    def stop(self):
        # Stop consuming new messages
        self.stopping = True
        # .stop() will wait until queued data will be really published
        super().stop()

    async def get_metrics_mappings(self):
        """
        Subscribe and track datastream changes
        """
        client = MetricsDataStreamClient("cfgmetrics", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track metrics settings")
            try:
                await client.query(
                    limit=config.metricscollector.ds_limit,
                    block=True,
                )
            except NOCError as e:
                self.logger.info("Failed to get metrics settings: %s", e)
                await asyncio.sleep(1)

    async def get_object_mappings(self):
        """Coroutine to request object mappings"""
        self.logger.info("Starting to track object mappings")
        client = SourceStreamClient("cfgmetricstarget", service=self)
        # Track stream changes
        while True:
            try:
                await client.query(
                    limit=config.metricscollector.ds_limit,
                    block=True,
                    filter_policy="delete",
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                await asyncio.sleep(1)

    async def on_ready(self) -> None:
        # Pass further initialization
        self.ready_event.set()

    async def update_metric_type(self, data: Dict[str, Any]) -> None:
        if data["id"] in self.id_mappings:
            self.update_data(data)
        else:
            self.insert_data(data)
        for ch in self.channels.values():
            ch.flush_unknown_metrics |= True

    async def delete_metric_type(self, mt_id: str) -> None:
        self.delete_data(mt_id)

    def insert_data(self, data: Dict[str, Any]) -> None:
        """
        Insert new data into tables
        """
        items = self.expand_rules(data)
        self.id_mappings[data["id"]] = items
        affected: Set[Tuple[str, str]] = {(i.collector, i.coll_field) for i in items}
        for i in items:
            if i.allow_partial_match:
                self.rx_mappings[i.collector, re.compile(i.coll_field)].append(i)
            else:
                self.mappings[i.collector, i.coll_field].append(i)
            for a in i.aliases or []:
                self.mappings[i.collector, a].append(i)
        # Reorder mappings according the preference
        for k in affected:
            self.mappings[k] = sorted(self.mappings[k], key=operator.attrgetter("preference"))

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Update data into tables
        """
        self.delete_data(data["id"])
        self.insert_data(data)

    def delete_data(self, mt_id: str) -> None:
        """
        Delete data from tables
        """
        items = self.id_mappings.get(mt_id) or []
        if not items:
            return
        affected: Set[Tuple[str, str]] = {(i.collector, i.coll_field) for i in items}
        for k in affected:
            self.mappings[k] = sorted(
                (i for i in self.mappings[k] if i.id != mt_id),
                key=operator.attrgetter("preference"),
            )
            if not self.mappings[k]:
                del self.mappings[k]
        del self.id_mappings[mt_id]

    async def update_sensors(self, cfg: SourceConfig, sensors: List[Dict[str, Any]]):
        """Update sensors Config"""
        processed = set()
        for data in sensors:
            s = SensorConfig.from_data(data, managed_object=cfg.bi_id)
            processed.add(s.id)
            self.sensor_configs[s.id] = s
            for m in s.get_mappings():
                self.source_map[m] = s.id
        if cfg.id not in self.source_configs:
            return
        for sid in self.source_configs[cfg.id].sensors or []:
            # Deleted
            if sid in processed or sid not in self.sensor_configs:
                continue
            # Clean mappings
            for m in self.sensor_configs[sid].get_mappings():
                if m in self.source_map:
                    del self.source_map[m]
            del self.sensor_configs[sid]

    async def update_remote_system(self, data):
        try:
            cfg = RemoteSystemConfig.from_data(data)
        except Exception:
            return
        self.remote_system_config[data["id"]] = cfg
        self.remote_system_map[cfg.api_key] = cfg.id
        self.remote_system_map[cfg.name.lower()] = cfg.id
        self.logger.info("[%s] Adding for received", cfg.name)
        # Update metrics
        metrics["sources_changed"] += 1
        self.add_sources += 1

    async def update_source(self, data):
        """Update Source config"""
        if data["type"] == "remote_system":
            return await self.update_remote_system(data)
        try:
            s = SourceConfig.from_data(data)
        except Exception as e:
            print(f"{data['id']} Error when processed source: {e}")
            return False
        if s.sensors or (s.id in self.sensor_configs and self.source_configs[s.id].sensors):
            await self.update_sensors(s, data.get("sensors"))
        if s.id not in self.source_configs:
            self.update_mappings(s.id, s.get_mappings())
        else:
            if not self.source_configs[s.id].is_diff(s):
                return False
            self.update_mappings(s.id, s.get_mappings(), self.source_configs[s.id].get_mappings())
        self.source_configs[s.id] = s
        # Update metrics
        metrics["sources_changed"] += 1
        self.add_sources += 1
        # Set Channel flags
        for ch in self.channels.values():
            ch.flush_unknown_hosts |= True

    def update_mappings(self, sid, new: Iterable[str], old: Optional[Iterable[str]] = None):
        """"""
        # Delete Old Mappings
        for m in set(old or []) - set(new):
            if m in self.source_map:
                del self.source_map[m]
        # Add new Mappings
        for m in set(new) - set(old or []):
            self.source_map[m] = sid

    async def delete_remote_system_config(self, sid):
        if sid not in self.remote_system_config:
            return
        cfg = self.remote_system_config.pop(sid)
        if cfg.name.lower() in self.remote_system_map:
            del self.remote_system_map[cfg.name.lower()]
        if cfg.api_key in self.remote_system_map:
            del self.remote_system_map[cfg.api_key]
        metrics["sources_deleted"] += 1

    async def delete_source(self, sid):
        await self.delete_remote_system_config(sid)
        if sid not in self.source_configs:
            return
        source = self.source_configs.pop(sid)
        for m in source.mapping_refs:
            if m in self.source_map:
                del self.source_map[m]
        for sid in source.sensors or []:
            cfg = self.sensor_configs.pop(sid, None)
            if not cfg:
                continue
            for m in cfg.get_mappings():
                if m in self.source_map:
                    del self.source_map[m]
        metrics["sources_deleted"] += 1

    async def on_event_source_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.event_source_ready.set()
        self.logger.info("%d Event Sources has been loaded", self.add_sources)
        # calculate size

    def lookup_source_by_name(
        self, name: str, collector: Optional[str] = None
    ) -> Optional[SourceConfig]:
        """Lookup source by name"""
        # Clean domain part
        hostname = name.split(".", 1)[0]
        # Lowe
        hostname = f"name:{hostname.lower()}"
        if hostname in self.source_map:
            return self.source_configs[self.source_map[hostname]]
        if f"name:{name.lower()}" in self.source_map:
            return self.source_configs[self.source_map[f"name:{name.lower()}"]]
        # Register invalid event source
        if self.source_configs and collector:
            metrics["error", ("type", "object_not_found"), ("collector", collector)] += 1
        else:
            metrics["error", ("type", "object_not_found")] += 1
        return None

    def lookup_remote_sensor(self, sid: str, remote_system: str) -> Optional[SensorConfig]:
        """Lookup remote_sensor"""
        if not self.sensor_configs:
            return None
        sid = f"rs:{remote_system}:{sid}"
        if sid in self.source_map:
            return self.sensor_configs[self.source_map[sid]]

    def lookup_agent_by_noc_key(self, key: str) -> Optional[SourceConfig]:
        """Lookup Agent by key"""
        if key in self.source_map:
            return self.source_configs[self.source_map[key]]
        metrics["error", ("type", "agent_not_found")] += 1
        return None

    def get_remote_system_by_code(
        self,
        code: str,
    ) -> Optional[RemoteSystemConfig]:
        """Check Remote System"""
        sid = self.remote_system_map.get(code.lower())
        if not sid or sid not in self.remote_system_config:
            return None
        return self.remote_system_config[sid]

    @cachetools.cachedmethod(operator.attrgetter("_rs_key_cache"))
    def get_remote_system_by_key(
        self,
        key: str,
    ) -> Optional[RemoteSystemConfig]:
        """Check Remote System"""
        for rs in self.remote_system_config.values():
            if rs.api_key == key:
                return rs
        return None

    @staticmethod
    def expand_rules(data: Dict[str, Any]) -> List[CfgItem]:
        return [
            CfgItem.from_data(
                rid=data["id"],
                table=data["table"],
                field=data["field"],
                data=item,
            )
            for item in data["rules"]
        ]

    def find_metrics_by_name(self, collector: str, name: str) -> List[CfgItem]:
        """Find by name (rx)"""
        if (collector, name) in self.mappings:
            return self.mappings[(collector, name)]
        if self.rx_mappings:
            # Find partial match
            return self.find_metrics_by_rx(collector, name)
        return []

    @cachetools.cachedmethod(operator.attrgetter("_rx_name_cache"))
    def find_metrics_by_rx(self, collector: str, name: str) -> List[CfgItem]:
        """Find metric by Alias rx"""
        r = []
        for (c, rx), cfgs in self.rx_mappings.items():
            if c != collector or not rx.match(name):
                continue
            r += cfgs
        return r

    def get_cfg_metric(
        self,
        collector,
        name,
        labels: Optional[List[str]] = None,
    ) -> Optional[CfgItem]:
        """Get Metric config"""
        if labels:
            labels = frozenset(labels)
        for m in self.find_metrics_by_name(collector, name):
            # all(rl in item_labels for rl in rule_labels)
            if labels and m.labels and m.labels - labels:
                continue
            return m
        # Not Mapped metric
        self.logger.debug("[%s] Not mapped value: %s. Skipping", collector, name)
        return None


if __name__ == "__main__":
    MetricsCollectorService().start()
