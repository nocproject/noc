#!./bin/python
# ----------------------------------------------------------------------
# Metrics service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections import defaultdict
from typing import Any, Dict, Tuple, List, Optional
import sys
import asyncio
import codecs
import hashlib
import random
import re

# Third-party modules
import orjson

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.liftbridge.message import Message
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.mongo.connection_async import connect_async
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.scope import MetricScopeCDAGFactory
from noc.services.metrics.changelog import ChangeLog
from noc.services.metrics.rule import iter_rules
from noc.services.metrics.datastream import MetricsDataStreamClient
from noc.config import config

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]

rx_var = re.compile(r"\{\s*(\S+)\s*\}")


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str]
    key_labels: Tuple[str]
    units: Dict[str, str]


@dataclass
class Card(object):
    __slots__ = ("probes", "senders")
    probes: Dict[str, BaseCDAGNode]
    senders: Tuple[BaseCDAGNode]


@dataclass
class ManagedObjectInfo(object):
    __slots__ = ("id", "fm_pool", "labels", "metric_labels")
    id: int
    fm_pool: str
    labels: Optional[List[str]]
    metric_labels: Optional[List[str]]


class MetricsService(FastAPIService):
    name = "metrics"
    use_mongo = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scopes: Dict[str, ScopeInfo] = {}
        self.scope_cdag: Dict[str, CDAG] = {}
        self.cards: Dict[MetricKey, Card] = {}
        self.graph: Optional[CDAG] = None
        self.change_log: Optional[ChangeLog] = None
        self.start_state: Dict[str, Dict[str, Any]] = {}
        self.mo_map: Dict[int, ManagedObjectInfo] = {}
        self.mappings_ready_event = asyncio.Event()
        self.dispose_partitions: Dict[str, int] = {}

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        self.change_log = ChangeLog(self.slot_number)
        connect_async()
        self.load_scopes()
        if config.metrics.compact_on_start:
            await self.change_log.compact()
        self.start_state = await self.change_log.get_state()
        self.graph = CDAG("metrics")
        if config.metrics.flush_interval > 0:
            asyncio.create_task(self.log_runner())
        if config.metrics.compact_interval > 0:
            asyncio.create_task(self.compact_runnner())
        # Start tracking changes
        asyncio.get_running_loop().create_task(self.get_object_mappings())
        # Subscribe metrics stream
        asyncio.get_running_loop().create_task(self.subscribe_metrics())

    async def subscribe_metrics(self) -> None:
        self.logger.info("Waiting for mappings")
        await self.mappings_ready_event.wait()
        self.logger.info("Mappings are ready")
        await self.subscribe_stream("metrics", self.slot_number, self.on_metrics)

    async def on_deactivate(self):
        if self.change_log:
            await self.change_log.flush()
            self.change_log = None
        if config.metrics.compact_on_stop:
            await self.change_log.compact()

    async def log_runner(self):
        self.logger.info("Run log runner")
        while True:
            await asyncio.sleep(config.metrics.flush_interval)
            if self.change_log:
                await self.change_log.flush()

    async def compact_runnner(self):
        self.logger.info("Run compact runner")
        # Randomize compaction on different slots to prevent the load spikes
        await asyncio.sleep(random.random() * config.metrics.compact_interval)
        while True:
            await self.change_log.compact()
            await asyncio.sleep(config.metrics.compact_interval)

    async def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = MetricsDataStreamClient("cfgmomapping", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                await client.query(
                    limit=config.metrics.ds_limit,
                    block=True,
                    filter_policy="delete",
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                await asyncio.sleep(1)

    async def on_metrics(self, msg: Message) -> None:
        data = orjson.loads(msg.value)
        state = {}
        for item in data:
            scope = item.get("scope")
            if not scope:
                self.logger.debug("Discard metric without scope: %s", item)
                metrics["discard", ("reason", "without_scope")] += 1
                return  # Discard metric without scope
            si = self.scopes.get(scope)
            if not si:
                self.logger.debug("Unknown scope: %s", item)
                metrics["discard", ("reason", "unknown_scope")] += 1
                return  # Unknown scope
            labels = item.get("labels") or []
            if si.key_labels and not labels:
                self.logger.debug("No labels: %s", item)
                metrics["discard", ("reason", "no_labels")] += 1
                return  # No labels
            mk = self.get_key(si, item)
            if si.key_fields and not mk[1]:
                self.logger.debug("No key fields: %s", item)
                metrics["discard", ("reason", "no_keyfields")] += 1
                return  # No key fields
            if si.key_labels and len(mk[2]) != len(si.key_labels):
                self.logger.debug("Missed key label: %s", item)
                metrics["discard", ("reason", "missed_keylabel")] += 1
                return  # Missed key label
            card = await self.get_card(mk, labels)
            if not card:
                self.logger.info("Cannot instantiate card: %s", item)
                return  # Cannot instantiate card
            state.update(self.activate_card(card, si, item))
        # Save state change
        if state:
            await self.change_log.feed(state)

    def load_scopes(self):
        """
        Load ScopeInfo structures
        :return:
        """
        units = defaultdict(dict)
        for mt in MetricType.objects.all():
            if mt.units:
                units[mt.scope.id][mt.field_name] = mt.units.code
        for ms in MetricScope.objects.all():
            self.logger.debug("Loading scope %s", ms.table_name)
            si = ScopeInfo(
                scope=ms.table_name,
                key_fields=tuple(sorted(kf.field_name for kf in ms.key_fields)),
                key_labels=tuple(sorted(kl.label[:-1] for kl in ms.labels if kl.is_required)),
                units=units[ms.id],
            )
            self.scopes[ms.table_name] = si
            self.logger.debug(
                "[%s] key fields: %s, key labels: %s", si.scope, si.key_fields, si.key_labels
            )

    @staticmethod
    def get_key(si: ScopeInfo, data: Dict[str, Any]) -> MetricKey:
        def iter_key_labels():
            labels = data.get("labels")
            if not labels or not si.key_labels:
                return
            scopes = {f'{ll.rsplit("::", 1)[0]}::': ll for ll in labels}
            for k in si.key_labels:
                v = scopes.get(k)
                if v is not None:
                    yield v

        return (
            si.scope,
            tuple((k, data[k]) for k in si.key_fields if k in data),
            tuple(iter_key_labels()),
        )

    @staticmethod
    def get_key_hash(k: MetricKey) -> str:
        """
        Calculate persistent hash for metric key
        """
        d = hashlib.sha512(str(k).encode("utf-8")).digest()
        return codecs.encode(d, "base-64")[:7].decode("utf-8")

    async def get_card(self, k: MetricKey, labels: List[str]) -> Optional[Card]:
        """
        Generate part of computation graph and collect its viable inputs
        :param k: (scope, ((key field, key value), ...), (key label, ...))
        :param labels: List of all labels

        :return:
        """
        card = self.cards.get(k)
        if card:
            return card
        # Generate new CDAG
        cdag = self.get_scope_cdag(k)
        if not cdag:
            return None
        # Apply CDAG to a common graph and collect inputs to the card
        card = await self.project_cdag(cdag, prefix=self.get_key_hash(k), k=k, labels=labels)
        self.cards[k] = card
        return card

    def get_scope_cdag(self, k: MetricKey) -> Optional[CDAG]:
        """
        Generate CDAG for a given metric key
        :param k:
        :return:
        """
        # @todo: Still naive implementation based around the scope
        # @todo: Must be replaced by profile-based card stack generator
        scope = k[0]
        if scope in self.scope_cdag:
            return self.scope_cdag[scope]
        # Not found, create new CDAG
        ms = MetricScope.objects.filter(table_name=k[0]).first()
        if not ms:
            return None  # Not found
        cdag = CDAG(f"scope::{k[0]}", {})
        factory = MetricScopeCDAGFactory(cdag, scope=ms, sticky=True)
        factory.construct()
        self.scope_cdag[k[0]] = cdag
        return cdag

    async def project_cdag(self, src: CDAG, prefix: str, k: MetricKey, labels: List[str]) -> Card:
        """
        Project `src` to a current graph and return the controlling Card
        :param src:
        :return:
        """

        def unscope(x):
            return sys.intern(x.rsplit("::", 1)[-1])

        def clone_and_add_node(
            n: BaseCDAGNode, config: Optional[Dict[str, Any]] = None
        ) -> BaseCDAGNode:
            """
            Clone node and add it to the graph
            """
            node_id = n.node_id
            state_id = f"{prefix}::{node_id}"
            state = self.start_state.pop(state_id, None)
            new_node = n.clone(node_id, prefix=prefix, state=state, config=config)
            nodes[node_id] = new_node
            return new_node

        def expand(s: str, ctx: Dict[str, Any]) -> str:
            return rx_var.sub(lambda x: str(ctx.get(x, "")), s)

        def merge_labels(l1: Optional[List[str]], l2: List[str]) -> List[str]:
            if not l1:
                return l2
            if not l2:
                return l1
            l2_set = set(l2)
            return l2[:] + [x for x in l1 if x not in l2_set]

        nodes: Dict[str, BaseCDAGNode] = {}
        # Clone nodes
        for node in src.nodes.values():
            clone_and_add_node(node)
        # Subscribe
        for o_node in src.nodes.values():
            node = nodes[o_node.node_id]
            for rs in o_node.iter_subscribers():
                node.subscribe(
                    nodes[rs.node.node_id], rs.input, dynamic=rs.node.is_dynamic_input(rs.input)
                )
        # Apply rules
        key_ctx = dict(k[1])
        if "managed_object" in key_ctx:
            mo_info = self.mo_map.get(key_ctx["managed_object"])
        else:
            mo_info = None
        if mo_info:
            mo_labels = mo_info.labels
        else:
            mo_labels = None
        for item in iter_rules(k[0], merge_labels(mo_labels, labels)):
            prev: Optional[BaseCDAGNode] = nodes.get(item.metric_type.field_name)
            if not prev:
                self.logger.error("Cannot find probe node %s", item.metric_type.field_name)
                continue
            if item.compose_node:
                compose_node = clone_and_add_node(item.compose_node)
                if item.compose_inputs:
                    for probe_name, input_name in item.compose_inputs.items():
                        probe_node = nodes.get(probe_name)
                        if not probe_node:
                            self.logger.error("Cannot find probe node %s", probe_node)
                            continue
                        probe_node.subscribe(compose_node, input_name)
                else:
                    prev.subscribe(compose_node, compose_node.first_input())
                prev = compose_node
            if item.activation_node:
                activation_node = clone_and_add_node(item.activation_node)
                prev.subscribe(activation_node, activation_node.first_input())
                prev = activation_node
            if item.alarm_node:
                # Expand key fields
                if not mo_info:
                    self.logger.error("Cannot find managed_object for %s. Skipping alarm node.", k)
                else:
                    # Collect labels
                    labels = item.alarm_node.config.labels or []
                    if k[2]:
                        labels += k[2]
                    # Expand config
                    n_parts = await self.get_dispose_partitions(mo_info.fm_pool)
                    alarm_config = {
                        "managed_object": str(mo_info.id),
                        "pool": mo_info.fm_pool,
                        "partition": mo_info.id % n_parts,
                        "reference": expand(item.alarm_node.config.reference, key_ctx),
                        "labels": labels or None,
                    }
                    # Clone alarm node
                    alarm_node = clone_and_add_node(item.alarm_node, config=alarm_config)
                    prev.subscribe(alarm_node, alarm_node.first_input())
                    prev = alarm_node
        # Compact the strorage
        for node in nodes.values():
            node.freeze()
        # Return resulting cards
        return Card(
            probes={unscope(node.node_id): node for node in nodes.values() if node.name == "probe"},
            senders=tuple(node for node in nodes.values() if node.name == "metrics"),
        )

    async def get_dispose_partitions(self, pool: str) -> int:
        """
        Returns an amount of dispose partitions
        """
        parts = self.dispose_partitions.get(pool)
        if parts is None:
            # Request partitions
            parts = await self.get_stream_partitions(f"dispose.{pool}")
            self.dispose_partitions[pool] = parts
        return parts

    def activate_card(
        self, card: Card, si: ScopeInfo, data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Activate card and return changed state
        """
        units = data.get("_units") or {}
        tx = self.graph.begin()
        ts = data["ts"]
        for n in data:
            mu = units.get(n) or si.units.get(n)
            if not mu:
                continue  # Missed field
            probe = card.probes.get(n)
            if not probe:
                continue
            probe.activate(tx, "ts", ts)
            probe.activate(tx, "x", data[n])
            probe.activate(tx, "unit", mu)
        # Activate senders
        for sender in card.senders:
            for kf in si.key_fields:
                kv = data.get(kf)
                if kv is not None:
                    sender.activate(tx, kf, kv)
            sender.activate(tx, "ts", ts)
            sender.activate(tx, "labels", data.get("labels") or [])
        return tx.get_changed_state()

    def update_mapping(
        self, mo_id: int, bi_id: int, fm_pool: str, labels: List[str], metric_labels: List[str]
    ) -> None:
        """
        Update managed object mapping.
        """
        self.mo_map[bi_id] = ManagedObjectInfo(
            id=mo_id,
            fm_pool=fm_pool,
            labels=[sys.intern(x) for x in labels],
            metric_labels=[sys.intern(x) for x in metric_labels],
        )

    def delete_mapping(self, bi_id: int) -> None:
        """
        Delete managed object mapping.
        """
        if bi_id in self.mo_map:
            del self.mo_map[bi_id]

    async def on_mappings_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.mappings_ready_event.set()


if __name__ == "__main__":
    MetricsService().start()
