#!./bin/python
# ----------------------------------------------------------------------
# metricscollector service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List, Dict, Set, DefaultDict
from collections import defaultdict
import operator

# NOC modules
import orjson

from noc.config import config
from noc.core.error import NOCError
from noc.core.perf import metrics
from noc.core.hash import hash_int
from noc.core.service.fastapi import FastAPIService
from noc.services.metricscollector.datastream import MetricsDataStreamClient
from noc.services.metricscollector.models.send import SendRequestItem

NS = 1_000_000_000


@dataclass(frozen=True)
class CfgItem(object):
    id: str
    ch_table: str
    ch_field: str
    collector: str
    coll_field: str
    labels: List[str]
    preference: int


class MetricsCollectorService(FastAPIService):
    name = "metricscollector"
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/metricscollector`)"

    def __init__(self):
        super().__init__()
        self.cfg_data: List[CfgItem] = []
        self.mappings: DefaultDict[Tuple[str, str], List[CfgItem]] = defaultdict(list)
        self.id_mappings: Dict[str, List[CfgItem]] = {}
        self.n_parts: int = 0
        self.ready_event: Optional[asyncio.Event] = None

    async def init_api(self):
        # Postpone initialization process until config datastream is fully processed
        self.ready_event = asyncio.Event()
        self.n_parts = await self.get_stream_partitions("metrics")
        asyncio.get_running_loop().create_task(self.get_metrics_mappings())
        # Set by datastream.on_ready
        await self.ready_event.wait()
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

    @staticmethod
    def expand_rules(data: Dict[str, Any]) -> List[CfgItem]:
        return [
            CfgItem(
                id=data["id"],
                ch_table=data["table"],
                ch_field=data["field"],
                collector=item["collector"],
                coll_field=item["field"],
                labels=item["labels"],
                preference=item["preference"],
            )
            for item in data["rules"]
        ]

    def insert_data(self, data: Dict[str, Any]) -> None:
        """
        Insert new data into tables
        :param data:
        :return:
        """
        items = self.expand_rules(data)
        self.cfg_data += items
        self.id_mappings[data["id"]] = items
        affected: Set[Tuple[str, str]] = {(i.collector, i.coll_field) for i in items}
        for i in items:
            self.mappings[i.collector, i.coll_field].append(i)
        # Reorder mappings according the preference
        for k in affected:
            self.mappings[k] = list(sorted(self.mappings[k], key=operator.attrgetter("preference")))

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Update data into tables
        :param data:
        :return:
        """
        self.delete_data(data["id"])
        self.insert_data(data)

    def delete_data(self, mt_id: str) -> None:
        """
        Delete data from tables
        :param mt_id:
        :return:
        """
        items = self.id_mappings.get(mt_id) or []
        if not items:
            return
        affected: Set[Tuple[str, str]] = {(i.collector, i.coll_field) for i in items}
        for k in affected:
            self.mappings[k] = list(
                sorted(
                    (i for i in self.mappings[k] if i.id != mt_id),
                    key=operator.attrgetter("preference"),
                )
            )
            if not self.mappings[k]:
                del self.mappings[k]
        del self.id_mappings[mt_id]

    def send_data(self, data: List[SendRequestItem]):
        """
        Apply mappings to the request item and spool the data
        :param data:
        :return:
        """

        def is_matched(rule_labels: List[str], item_labels: List[str]) -> bool:
            for rl in rule_labels:
                if rl not in item_labels:
                    return False
            return True

        r: List[Dict[str, Any]] = []
        for item in data:
            metrics["items"] += 1
            out: Dict[str, Dict[str, Any]] = {}
            units = item.metrics.get("_units", {})
            for coll_field, value in item.metrics.items():
                if coll_field == "_units":
                    continue
                if (item.collector, coll_field) not in self.mappings:
                    # Not Mapped metric
                    self.logger.debug(
                        "[%s] Not mapped value: %s. Skipping", item.collector, coll_field
                    )
                    continue
                for map_item in self.mappings.get((item.collector, coll_field)):
                    metrics["values"] += 1
                    if not is_matched(map_item.labels, item.labels):
                        self.logger.info("Labels %s is not match. Skipping metric", item.labels)
                        continue
                    # Matched rule found
                    if map_item.ch_table not in out:
                        out[map_item.ch_table] = {
                            "ts": (item.ts.timestamp() + config.tz_utc_offset) * NS,
                            "scope": map_item.ch_table,
                            "labels": item.labels,
                            "service": item.service,
                            "_units": {},
                        }
                    out[map_item.ch_table][map_item.ch_field] = value
                    if coll_field in units:
                        out[map_item.ch_table]["_units"][map_item.ch_field] = units[coll_field]
                    metrics["mapped_values"] += 1
                    break
            # Spool data
            r += list(out.values())
        # Split to partitions
        parts = defaultdict(list)
        for item in r:
            key = hash_int(item["service"])
            parts[key % self.n_parts].append(item)
        # Spool data
        for partition, items in parts.items():
            self.publish(orjson.dumps(items), stream="metrics", partition=partition)


if __name__ == "__main__":
    MetricsCollectorService().start()
