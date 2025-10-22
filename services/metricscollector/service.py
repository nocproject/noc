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
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List, Dict, Set, Iterable, DefaultDict, FrozenSet
from collections import defaultdict

# Third-party modules
import cachetools
import orjson

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.perf import metrics
from noc.core.service.fastapi import FastAPIService
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.nodatachecker import NoDataChecker
from noc.services.metricscollector.datastream import MetricsDataStreamClient, SourceStreamClient
from noc.services.metricscollector.models.sendmetric import SendMetric
from noc.services.metricscollector.sourceconfig import SourceConfig

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
            labels=data["labels"],
            aliases=data["aliases"],
            preference=data["preference"],
        )


class MetricsCollectorService(FastAPIService):
    name = "metricscollector"
    # use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/metricscollector`)"
    # Cache regex for partial match
    _rx_name_cache = cachetools.LRUCache(500)

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
        self.source_configs: Dict[str, SourceConfig] = {}  # id -> SourceConfig
        self.source_map: Dict[str, str] = {}
        self.invalid_sources = defaultdict(int)  # ip -> count
        self.banned_rs = set()
        self.remote_system_map: Dict[str, str] = {}

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
        self.report_invalid_callback = PeriodicCallback(self.report_invalid_sources, 60000)
        self.report_invalid_callback.start()
        if config.metricscollector.nodata_round_duration:
            self.no_data_checker.initialize()
        # For used MX service
        self.mx_partitions = await self.get_stream_partitions("message") or 0
        # Process as usual
        await super().init_api()

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
        """
        Coroutine to request object mappings
        """
        self.logger.info("Starting to track object mappings")
        client = SourceStreamClient("cfgtarget", service=self)
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

    async def delete_metric_type(self, mt_id: str) -> None:
        self.delete_data(mt_id)

    async def update_source(self, data):
        """Update Source config"""
        try:
            s = SourceConfig.from_data(data)
        except Exception as e:
            print(f"{data['id']}Error when processed source: {e}")
            return False
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
        for m in data.get("mapping_refs") or []:
            code, *refs = m.split(":")
            if code == "rs" and refs[0].lower() not in self.remote_system_map:
                self.remote_system_map[refs[0].lower()] = refs[0]

    def update_mappings(self, sid, new: Iterable[str], old: Optional[Iterable[str]] = None):
        """"""
        # Delete Old Mappings
        for m in set(old or []) - set(new):
            if m in self.source_map:
                del self.source_map[m]
        # Add new Mappings
        for m in set(new) - set(old or []):
            self.source_map[m] = sid

    async def delete_source(self, sid):
        if sid not in self.source_configs:
            return False
        source = self.source_configs.pop(sid)
        for m in source.mapping_refs:
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
        name = name.split(".", 1)[0]
        # Lowe
        name = f"name:{name.lower()}"
        if name in self.source_map:
            return self.source_configs[self.source_map[name]]
        # Register invalid event source
        if self.source_configs and collector:
            metrics["error", ("type", "object_not_found"), ("collector", collector)] += 1
        else:
            metrics["error", ("type", "object_not_found")] += 1
        self.invalid_sources[name] += 1
        return None

    def lookup_agent_by_noc_key(self, key: str) -> Optional[SourceConfig]:
        """Lookup Agent by key"""
        if key in self.source_map:
            return self.source_configs[self.source_map[key]]
        metrics["error", ("type", "agent_not_found")] += 1
        self.invalid_sources[key] += 1
        return None

    def get_remote_system_name(self, code, authorization: Optional[str] = None) -> Optional[str]:
        """Check Remote System"""
        if code.lower() not in self.remote_system_map:
            return None
        return self.remote_system_map[code.lower()]

    def is_rs_banned(self, code) -> bool:
        """Check remote system is banned"""
        return code in self.banned_rs

    def ban_remote_system(self, code):
        """Add Remote System code to banned"""
        self.logger.warning("[%s] Add RemoteSystem code to banned", code)
        self.banned_rs.add(code)

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
            if labels and m.labels and labels - m.labels:
                continue
            return m
        # Not Mapped metric
        self.logger.debug("[%s] Not mapped value: %s. Skipping", collector, name)
        return None

    def send_data(self, data: List[SendMetric]):
        """
        Apply mappings to the request item and spool the data
        """
        parts = defaultdict(list)
        for item in data:
            metrics["items"] += 1
            out: Dict[str, Dict[str, Any]] = {}
            units = item.metrics.get("_units", {})
            for coll_field, value in item.metrics.items():
                if coll_field == "_units":
                    continue
                metrics["values"] += 1
                cfg_metric = self.get_cfg_metric(item.collector, coll_field, labels=item.labels)
                if not cfg_metric:
                    # Unknown metric field
                    continue
                # Matched rule found
                if cfg_metric.ch_table not in out:
                    out[cfg_metric.ch_table] = {
                        "ts": (item.ts.timestamp() + config.tz_utc_offset) * NS,
                        "scope": cfg_metric.ch_table,
                        "labels": item.labels,
                        "service": item.service,
                        "managed_object": item.managed_object,
                        "s_key": item.key,
                        "_units": {},
                    }
                    if item.remote_system:
                        out[cfg_metric.ch_table]["remote_system"] = item.remote_system
                out[cfg_metric.ch_table][cfg_metric.ch_field] = value
                if coll_field in units:
                    out[cfg_metric.ch_table]["_units"][cfg_metric.ch_field] = units[coll_field]
                metrics["mapped_values"] += 1
            # Spool data
            # Split to partitions
            parts[item.key % self.n_parts] += out.values()
        # Spool data
        for partition, items in parts.items():
            self.publish(orjson.dumps(items), stream="metrics", partition=partition)


if __name__ == "__main__":
    MetricsCollectorService().start()
