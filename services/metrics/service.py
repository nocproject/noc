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
from typing import Any, Dict, Tuple, List, Optional, Set
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
from noc.core.cdag.node.probe import ProbeNode, ProbeNodeConfig
from noc.core.cdag.node.alarm import AlarmNode
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.scope import MetricScopeCDAGFactory
from noc.services.metrics.changelog import ChangeLog
from noc.services.metrics.datastream import MetricsDataStreamClient
from noc.config import config as global_config

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]

rx_var = re.compile(r"\{\s*(\S+)\s*\}")


def unscope(x):
    return sys.intern(x.rsplit("::", 1)[-1])


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str, ...]
    key_labels: Tuple[str, ...]
    units: Dict[str, str]


@dataclass
class Card(object):
    __slots__ = ("alarm", "probes", "senders")
    probes: Dict[str, BaseCDAGNode]
    senders: Tuple[BaseCDAGNode]
    alarms: List[AlarmNode]

    def get_sender(self, name: str) -> Optional[BaseCDAGNode]:
        """
        Get probe sender by name
        :param name:
        :return:
        """
        return next((s for s in self.senders if s.config.scope == name), None)


@dataclass
class Rule(object):
    match_labels: Set[str]
    nodes: List[BaseCDAGNode]
    configs: Dict[str, Any]  # NodeId -> Config

    def is_matched(self, labels: Set[str]) -> bool:
        return labels.issuperset(self.match_labels)


@dataclass
class ManagedObjectInfo(object):
    __slots__ = ("id", "bi_id", "fm_pool", "labels", "metric_labels")
    id: int
    bi_id: int
    fm_pool: str
    labels: Optional[List[str]]
    metric_labels: Optional[List[str]]


class MetricsService(FastAPIService):
    name = "metrics"
    use_mongo = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scopes: Dict[str, ScopeInfo] = {}
        self.metric_configs: Dict[str, ProbeNodeConfig] = {}
        self.scope_cdag: Dict[str, CDAG] = {}
        self.cards: Dict[MetricKey, Card] = {}
        self.graph: Optional[CDAG] = None
        self.change_log: Optional[ChangeLog] = None
        self.start_state: Dict[str, Dict[str, Any]] = {}
        self.mo_map: Dict[int, ManagedObjectInfo] = {}
        self.mo_id_map: Dict[int, ManagedObjectInfo] = {}
        self.mappings_ready_event = asyncio.Event()
        self.dispose_partitions: Dict[str, int] = {}
        self.rules: Dict[str, Rule] = {}  # Action -> Graph Config
        self.lazy_init: bool = True
        self.disable_spool: bool = False

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        self.change_log = ChangeLog(self.slot_number)
        connect_async()
        self.load_scopes()
        if global_config.metrics.compact_on_start:
            await self.change_log.compact()
        self.start_state = await self.change_log.get_state()
        self.graph = CDAG("metrics")
        if global_config.metrics.flush_interval > 0:
            asyncio.create_task(self.log_runner())
        if global_config.metrics.compact_interval > 0:
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
            if global_config.metrics.compact_on_stop:
                await self.change_log.compact()
            self.change_log = None

    async def log_runner(self):
        self.logger.info("Run log runner")
        while True:
            await asyncio.sleep(global_config.metrics.flush_interval)
            if self.change_log:
                await self.change_log.flush()

    async def compact_runnner(self):
        self.logger.info("Run compact runner")
        # Randomize compaction on different slots to prevent the load spikes
        await asyncio.sleep(random.random() * global_config.metrics.compact_interval)
        while True:
            await self.change_log.compact()
            await asyncio.sleep(global_config.metrics.compact_interval)

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
                    limit=global_config.metrics.ds_limit,
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
            state.update(self.activate_card(card, si, mk, item))
        # Save state change
        if state:
            await self.change_log.feed(state)

    def load_scopes(self):
        """
        Load ScopeInfo structures
        :return:
        """
        units: Dict[str, Dict[str, str]] = defaultdict(dict)
        for mt in MetricType.objects.all():
            if mt.units:
                units[mt.scope.id][mt.field_name] = mt.units.code
            self.metric_configs[mt.field_name] = ProbeNodeConfig(
                unit=(mt.units.code or "1") if mt.units else "1",
                scale=mt.scale.code if mt.scale else "1",
            )
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

    def load_rules(self):
        """

        :return:
        """
        from noc.pm.models.metricrule import MetricRule

        for mr in MetricRule.objects.filter(is_active=True):
            for item in mr.items:
                if not item.is_active:
                    continue
                ma = item.metric_action.get_config()
                self.rules[f"{mr.name}-{ma.name}"] = Rule(
                    match_labels=set(sys.intern(label) for label in mr.match_labels),
                    nodes=ma.nodes,
                    configs={node.node_id: node.config for node in ma.nodes if node.config},
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
        card = await self.project_cdag(cdag, prefix=self.get_key_hash(k))
        metrics["project_cards"] += 1
        self.cards[k] = card
        self.apply_rules(k, labels)
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
        factory = MetricScopeCDAGFactory(
            cdag, scope=ms, sticky=True, spool=not self.disable_spool, lazy_init=self.lazy_init
        )
        factory.construct()
        self.scope_cdag[k[0]] = cdag
        return cdag

    def clone_and_add_node(
        self, n: BaseCDAGNode, prefix: str, config: Optional[Dict[str, Any]] = None
    ) -> BaseCDAGNode:
        """
        Clone node and add it to the graph
        """
        node_id = n.node_id
        state_id = f"{prefix}::{node_id}"
        state = self.start_state.pop(state_id, None)
        new_node = n.clone(node_id, prefix=prefix, state=state, config=config)
        # nodes[node_id] = new_node
        metrics["cdag_nodes", ("type", n.name)] += 1
        return new_node

    async def project_cdag(self, src: CDAG, prefix: str) -> Card:
        """
        Project `src` to a current graph and return the controlling Card
        :param src:
        :param prefix:
        :return:
        """

        nodes: Dict[str, BaseCDAGNode] = {}
        # Clone nodes
        for node in src.nodes.values():
            nodes[node.node_id] = self.clone_and_add_node(node, prefix=prefix)
        # Subscribe
        for o_node in src.nodes.values():
            node = nodes[o_node.node_id]
            for rs in o_node.iter_subscribers():
                node.subscribe(
                    nodes[rs.node.node_id], rs.input, dynamic=rs.node.is_dynamic_input(rs.input)
                )
        # Compact the storage
        for node in nodes.values():
            node.freeze()
        # Return resulting cards
        return Card(
            probes={unscope(node.node_id): node for node in nodes.values() if node.name == "probe"},
            senders=tuple(node for node in nodes.values() if node.name == "metrics"),
            alarms=[],
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

    def add_probe(self, metric_field: str, k: MetricKey) -> Optional[ProbeNode]:
        card = self.cards[k]
        mt = MetricType.get_by_field_name(metric_field)
        if not mt:
            return None
        sender = card.get_sender(mt.scope.table_name)
        if not sender:
            return
        prefix = self.get_key_hash(k)
        state_id = f"{self.get_key_hash(k)}::{metric_field}"
        # Create Probe
        p = ProbeNode.construct(
            metric_field,
            prefix=prefix,
            state=self.start_state.get(state_id),
            config=self.metric_configs.get(metric_field),
            sticky=True,
        )
        # Subscribe
        p.subscribe(sender, metric_field, dynamic=True)
        p.freeze()
        card.probes[unscope(metric_field)] = p
        #
        metrics["cdag_nodes", ("type", "probe")] += 1
        return p

    def apply_rules(self, k: MetricKey, labels: List[str]):
        """
        Apply rule structure
        :param k:
        :param labels:
        :return:
        """
        card = self.cards[k]
        s_labels = set(labels)
        for rule in self.rules.values():
            if not rule.is_matched(s_labels):
                continue
            nodes = {}
            # Node
            for node in rule.nodes:
                if node.name == "probe" and node.node_id in card.probes:
                    nodes[node.node_id] = card.probes[node.node_id]
                    continue
                elif node.name == "probe" and node.node_id not in card.probes:
                    # Metrics probe is not initialized yet ?add_probe
                    self.add_probe(node.node_id, k)
                    nodes[node.node_id] = card.probes[node.node_id]
                    break
                nodes[node.node_id] = self.clone_and_add_node(
                    node, prefix="xxx", config=rule.config.get(node.node_id)
                )
            if "alarm" not in nodes or "probe" not in nodes:
                self.logger.warning("Rules without ending output. Skipping")
                continue

            # Subscribe
            # Complex Node subscribe to sender
            # Probe node resubscribe to probe
            for o_node in rule.nodes:
                node = nodes[o_node.node_id]
                for rs in o_node.iter_subscribers():
                    node.subscribe(
                        nodes[rs.node.node_id], rs.input, dynamic=rs.node.is_dynamic_input(rs.input)
                    )
            card.alarms += [nodes["alarm"]]

    def activate_card(
        self, card: Card, si: ScopeInfo, k: MetricKey, data: Dict[str, Any]
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
            if self.lazy_init and not probe:
                probe = self.add_probe(n, k)
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
            bi_id=bi_id,
            fm_pool=fm_pool,
            labels=[sys.intern(x) for x in labels],
            metric_labels=[sys.intern(x) for x in metric_labels],
        )
        self.mo_id_map[mo_id] = self.mo_map[bi_id]

    def delete_mapping(self, mo_id: int) -> None:
        """
        Delete managed object mapping.
        """
        if mo_id in self.mo_id_map:
            del self.mo_map[self.mo_id_map[mo_id].bi_id]
            del self.mo_id_map[mo_id]

    async def on_mappings_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.mappings_ready_event.set()


if __name__ == "__main__":
    MetricsService().start()
