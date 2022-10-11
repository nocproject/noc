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
from typing import Any, Dict, Tuple, List, Optional, Set, Iterable, FrozenSet, Literal
import sys
import asyncio
import codecs
import hashlib
import random

# Third-party modules
import orjson
import cachetools
from pymongo import DESCENDING

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
from noc.core.cdag.node.composeprobe import ComposeProbeNode, ComposeProbeNodeConfig
from noc.core.cdag.node.alarm import AlarmNode, VarItem
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.scope import MetricScopeCDAGFactory
from noc.core.cdag.factory.config import ConfigCDAGFactory, GraphConfig
from noc.services.metrics.changelog import ChangeLog
from noc.services.metrics.datastream import MetricsDataStreamClient, MetricRulesDataStreamClient
from noc.services.datastream.streams.cfgmetricsources import CfgMetricSourcesDataStream
from noc.config import config as global_config

# MetricKey - scope, key ctx: (managed_object, <bi_id>), Key Labels
MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


def unscope(x):
    return sys.intern(x.rsplit("::", 1)[-1])


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str, ...]
    key_labels: Tuple[str, ...]
    units: Dict[str, str]
    enable_timedelta: bool = False


@dataclass
class Card(object):
    """
    Store Input probe nodes
    """

    __slots__ = ("alarms", "probes", "senders", "is_dirty", "affected_rules")
    probes: Dict[str, BaseCDAGNode]
    senders: Tuple[BaseCDAGNode]
    alarms: List[AlarmNode]
    affected_rules: Set[str]
    is_dirty: bool

    def get_sender(self, name: str) -> Optional[BaseCDAGNode]:
        """
        Get probe sender by name
        :param name:
        :return:
        """
        return next((s for s in self.senders if s.config.scope == name), None)

    @classmethod
    def iter_subscribed_nodes(cls, node) -> Iterable[BaseCDAGNode]:
        """
        Iterate over nodes subscribed to Probes on Card
        :return:
        """
        for s in node.iter_subscribers():
            yield s.node
            yield from cls.iter_subscribed_nodes(s.node)

    def invalidate_card(self):
        """
        Remove all subscribed node and set  is_dirty for applied rules
        :return:
        """
        for probe in self.probes.values():
            for node in self.iter_subscribed_nodes(probe):
                if node in self.senders or node in self.probes or node in self.alarms:
                    continue
                metrics["cdag_nodes", ("type", node.name)] -= 1
                del node
            # Cleanup Subscribe
            for s in list(probe.iter_subscribers()):
                if s.node in self.senders or s.node in self.probes or s.node in self.alarms:
                    continue
                probe.unsubscribe(s.node, s.input)
        self.set_dirty()

    def set_dirty(self):
        self.is_dirty = True


@dataclass
class Rule(object):
    """
    Store Rule actions, configs and conditions
    """

    id: str
    match_labels: FrozenSet[FrozenSet[str]]
    exclude_labels: Optional[FrozenSet[FrozenSet[str]]]
    match_scopes: Set[str]
    graph: CDAG
    configs: Dict[str, Dict[str, Any]]  # NodeId -> Config

    def is_matched(self, labels: Set[str]) -> bool:
        return any(labels.issuperset(ml) for ml in self.match_labels)

    def is_differ(self, rule: "Rule") -> FrozenSet[str]:
        """
        Diff nodes config - update configs only
        Diff graph nodes or structure - rebuld Card Rules
        Diff condition - rebuild or remove Card Rules
        :return:
        """
        r = []
        if set(self.graph.nodes) != set(rule.graph.nodes):
            # If compare Graph Node config always diff if change
            r.append("graph")
        if self.match_labels != rule.match_labels:
            r.append("conditions")
        if self.configs != rule.configs:
            r.append("configs")
        return frozenset(r)

    def update_config(self, configs: Dict[str, Dict[str, Any]]) -> Set[str]:
        """
        Update node config, return changed node
        :param configs:
        :return:
        """
        update_configs = set()
        for node_id in configs:
            if node_id in self.configs and self.configs[node_id] != configs[node_id]:
                self.configs[node_id].update(configs[node_id])
                update_configs.add(node_id)
            else:
                self.configs[node_id] = configs[node_id]
        return update_configs


@dataclass(frozen=True)
class ItemConfig(object):
    """
    Metric Source Item Config
    Match by key_labels
    """

    __slots__ = ("key_labels", "metric_labels", "metrics", "composed_metrics")
    key_labels: Tuple[str, ...]  # noc::interface::*, noc::interface::Fa 0/24
    metric_labels: Optional[Tuple[str, ...]]
    metrics: Tuple[str, ...]  # Metric Field list setting on source
    composed_metrics: Tuple[str, ...]  # Metric Field for compose metrics

    def is_match(self, k: MetricKey) -> bool:
        return not set(self.key_labels) - set(k[2])


@dataclass(frozen=True)
class SourceConfig(object):
    """
    Configuration for Metric Source and Items.
    Contains configured metrics, labels and alarm node config
    Supported Source:
    * managed_object
    * agent
    * sla_probe
    * sensor
    """

    __slots__ = ("type", "bi_id", "fm_pool", "labels", "metrics", "items")
    type: Literal["managed_object", "sla_probe", "sensor", "agent"]
    bi_id: int
    fm_pool: str
    labels: Optional[Tuple[str]]
    metrics: Tuple[str]
    items: List[ItemConfig]

    def is_differ(self, sc: "SourceConfig"):
        """
        Compare Source Config
        * condition - Diff labels
        * items - Diff items
        * metrics (additional Compose Metrics)
        :param sc:
        :return:
        """
        r = []
        if set(self.labels).difference(sc.labels):
            r += ["condition"]
        return r


@dataclass(frozen=True)
class SourceInfo(object):
    """
    Source Info for applied metric Card
    """

    __slots__ = (
        "bi_id",
        "sensor",
        "sla_probe",
        "fm_pool",
        "labels",
        "metric_labels",
        "composed_metrics",
    )
    bi_id: int
    fm_pool: str
    sla_probe: Optional[str]
    sensor: Optional[str]
    labels: Optional[List[str]]
    metric_labels: Optional[List[str]]
    composed_metrics: Optional[List[str]]


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

    def __init__(self):
        super().__init__()
        self.scopes: Dict[str, ScopeInfo] = {}
        self.metric_configs: Dict[Tuple[str, str], ProbeNodeConfig] = {}
        self.compose_inputs: Dict[str, Set] = {}
        self.scope_cdag: Dict[str, CDAG] = {}
        self.cards: Dict[MetricKey, Card] = {}
        self.graph: Optional[CDAG] = None
        self.change_log: Optional[ChangeLog] = None
        self.start_state: Dict[str, Dict[str, Any]] = {}
        self.sources_config: Dict[int, SourceConfig] = {}
        self.mappings_ready_event = asyncio.Event()
        self.rules_ready_event = asyncio.Event()
        self.dispose_partitions: Dict[str, int] = {}
        self.rules: Dict[str, Rule] = {}  # Action -> Graph Config
        self.lazy_init: bool = True
        self.disable_spool: bool = global_config.metrics.disable_spool
        self.source_metrics: Dict[Tuple[str, int], List[MetricKey]] = defaultdict(list)

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
        asyncio.get_running_loop().create_task(self.get_metric_rules_mappings())
        asyncio.get_running_loop().create_task(self.get_object_mappings())
        # Subscribe metrics stream
        asyncio.get_running_loop().create_task(self.subscribe_metrics())

    async def subscribe_metrics(self) -> None:
        self.logger.info("Waiting for rules")
        await self.rules_ready_event.wait()
        self.logger.info("Mappings are ready")
        await self.subscribe_stream("metrics", self.slot_number, self.on_metrics, async_cursor=True)

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
        client = MetricsDataStreamClient("cfgmetricsources", service=self)
        coll = CfgMetricSourcesDataStream.get_collection()
        r = next(coll.find({}).sort([("change_id", DESCENDING)]), None)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                await client.query(
                    change_id=str(r["change_id"]) if "change_id" in r else None,
                    limit=global_config.metrics.ds_limit,
                    block=True,
                    filter_policy="delete",
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                await asyncio.sleep(1)

    async def get_metric_rules_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = MetricRulesDataStreamClient("cfgmetricrules", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track metric rules")
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
        metrics["messages"] += 1
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
            if mt.compose_expression:
                self.metric_configs[(mt.scope.table_name, mt.field_name)] = ComposeProbeNodeConfig(
                    unit=(mt.units.code or "1") if mt.units else "1",
                    expression=mt.compose_expression,
                )
                self.compose_inputs[mt.field_name] = {m_t.field_name for m_t in mt.compose_inputs}
                continue
            self.metric_configs[(mt.scope.table_name, mt.field_name)] = ProbeNodeConfig(
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
                enable_timedelta=ms.enable_timedelta,
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
    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60))
    def get_key_hash(k: MetricKey) -> str:
        """
        Calculate persistent hash for metric key
        """
        d = hashlib.blake2b(str(k).encode("utf-8")).digest()
        return codecs.encode(d, "base_64")[:7].decode("utf-8")

    @staticmethod
    def merge_labels(l1: Optional[List[str]], l2: List[str]) -> List[str]:
        """
        Merge labels list
        :param l1:
        :param l2:
        :return:
        """
        if not l1:
            return l2
        if not l2:
            return l1
        l2_set = set(l2)
        return l2[:] + [x for x in l1 if x not in l2_set]

    async def get_card(self, k: MetricKey, labels: List[str]) -> Optional[Card]:
        """
        Generate part of computation graph and collect its viable inputs
        :param k: (scope, ((key field, key value), ...), (key label, ...))
        :param labels: List of all labels

        :return:
        """
        card = self.cards.get(k)

        if card and card.is_dirty:
            # Apply Rules after invalidate cache
            self.apply_rules(k, labels)
            return card
        elif card:
            return card
        # Generate new CDAG
        cdag = self.get_scope_cdag(k)
        if not cdag:
            return None
        # Apply CDAG to a common graph and collect inputs to the card
        card = await self.project_cdag(cdag, prefix=self.get_key_hash(k))
        metrics["project_cards"] += 1
        self.cards[k] = card
        self.source_metrics[k[1][-1]].append(k)
        # Apply Rules
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
        self,
        n: BaseCDAGNode,
        prefix: str,
        config: Optional[Dict[str, Any]] = None,
        static_config=None,
    ) -> BaseCDAGNode:
        """
        Clone node without subscribers and apply state and config
        """
        state_id = f"{prefix}::{n.node_id}"
        state = self.start_state.pop(state_id, None)
        new_node = n.clone(
            n.node_id, prefix=prefix, state=state, config=config, static_config=static_config
        )
        metrics["cdag_nodes", ("type", n.name)] += 1
        return new_node

    async def project_cdag(self, src: CDAG, prefix: str) -> Card:
        """
        Project `src` to a current graph and return the controlling Card
        :param src: Applied graph
        :param prefix: Unique card prefix
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
            affected_rules=set(),
            is_dirty=False,
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

    def add_probe(
        self, metric_field: str, k: MetricKey, is_composed: bool = False
    ) -> Optional[ProbeNode]:
        """
        Add new probe to card
        :param metric_field: Metric field name
        :param k: Metric key
        :param is_composed: Create ComposeProbeNode
        :return:
        """
        card = self.cards[k]
        mt = MetricType.get_by_field_name(metric_field, k[0])
        if not mt:
            self.logger.warning("[%s] Unknown metric field: %s", k, metric_field)
            return None
        sender = card.get_sender(mt.scope.table_name)
        if not sender:
            self.logger.debug("[%s] Sender is not found on Card: %s", k, mt.scope.table_name)
            return None
        probe_cls = ProbeNode
        if is_composed:
            probe_cls = ComposeProbeNode
        prefix = self.get_key_hash(k)
        state_id = f"{prefix}::{metric_field}"
        # Create Probe
        p = probe_cls.construct(
            metric_field,
            prefix=prefix,
            state=self.start_state.pop(state_id, None),
            config=self.metric_configs.get((k[0], metric_field)),
            sticky=True,
        )
        # Subscribe
        p.subscribe(sender, metric_field, dynamic=True, mark_bound=False)
        p.freeze()
        card.probes[unscope(metric_field)] = p
        #
        metrics["cdag_nodes", ("type", p.name)] += 1
        return p

    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60))
    def get_source(self, s_id):
        coll = CfgMetricSourcesDataStream.get_collection()
        data = coll.find_one({"_id": str(s_id)})
        if not data:
            return
        return self.get_source_config(orjson.loads(data["data"]))

    def get_source_info(self, k: MetricKey) -> Optional[SourceInfo]:
        """
        Get source Info by Metric Key. Sources:
         * managed_object
         * agent
         * sensor
         * sla_probe
        :param k: MetricKey
        :return:
        """
        key_ctx, source = dict(k[1]), None
        sensor, sla_probe = None, None
        if "sensor" in key_ctx:
            source = self.get_source(key_ctx["sensor"])
            # sensor = self.sources_config.get(key_ctx["sensor"])
        elif "sla_probe" in key_ctx:
            source = self.get_source(key_ctx["sla_probe"])
            # sla_probe = self.sources_config.get(key_ctx["sla_probe"])
        if "agent" in key_ctx:
            source = self.get_source(key_ctx["agent"])
            # source = self.sources_config.get(key_ctx["agent"])
        elif "managed_object" in key_ctx:
            source = self.get_source(key_ctx["managed_object"])
            # source = self.sources_config.get(key_ctx["managed_object"])
        if not source:
            return
        composed_metrics = []
        # Find matched item
        for item in source.items:
            if not item.is_match(k):
                continue
            if item.composed_metrics:
                composed_metrics = list(item.composed_metrics)
            break
        return SourceInfo(
            bi_id=source.bi_id,
            sensor=sensor,
            sla_probe=sla_probe,
            fm_pool=source.fm_pool,
            labels=list(source.labels),
            metric_labels=[],
            composed_metrics=composed_metrics,
        )

    def apply_rules(self, k: MetricKey, labels: List[str]):
        """
        Apply rule Graph
        :param k: Metric key
        :param labels: Metric labels
        :return:
        """
        card = self.cards[k]
        # Getting Context
        source = self.get_source_info(k)
        if not source:
            self.logger.debug("[%s] Unknown metric source. Skipping apply rules", k)
            metrics["unknown_metric_source"] += 1
            return
        s_labels = set(self.merge_labels(source.labels, labels))
        # Appy matched rules
        for rule_id, rule in self.rules.items():
            if k[0] not in rule.match_scopes or not rule.is_matched(s_labels):
                continue
            nodes: Dict[str, BaseCDAGNode] = {}
            # Node
            for node in rule.graph.nodes.values():
                # namespace, node_id split for connect to card probe
                ns, node_id = node.node_id.rsplit("::", 1)
                if node.name == "probe" and node_id in card.probes:
                    # Probe node, will be replaced to Card probes
                    nodes[node.node_id] = card.probes[node_id]
                    continue
                elif (
                    node.name == "probe"
                    and node_id not in card.probes
                    and "compose_" not in node_id
                ):
                    # Metrics probe is not initialized yet, add_probe. Skip compose  metric node
                    probe = self.add_probe(node_id, k)
                    nodes[node.node_id] = probe
                    continue
                config = rule.configs.get(node.node_id)
                static_config = None
                if node.name == "alarm":
                    slots = self.get_slot_limits(f"correlator-{source.fm_pool}")
                    static_config = {
                        "managed_object": f"bi_id:{source.bi_id}",
                        "partition": source.bi_id % slots or 0,
                        "pool": source.fm_pool,
                        "labels": k[2],
                    }
                    if source.sla_probe:
                        static_config["sla_probe"] = source.sla_probe
                    if source.sensor:
                        static_config["sensor"] = source.sensor
                nodes[node.node_id] = self.clone_and_add_node(
                    node, prefix=self.get_key_hash(k), config=config, static_config=static_config
                )
            if f"{rule_id}::alarm" not in nodes and f"{rule_id}::probe" not in nodes:
                self.logger.warning(
                    "[%s] Rules without ending output. Skipping", rule.graph.graph_id
                )
                continue
            # Subscribe
            # Probe node resubscribe to probe
            for o_node in rule.graph.nodes.values():
                node = nodes[o_node.node_id]
                for rs in o_node.iter_subscribers():
                    node.subscribe(
                        nodes[rs.node.node_id],
                        rs.input,
                        dynamic=rs.node.is_dynamic_input(rs.input),
                        mark_bound=False,
                    )
                if "_compose" in node.node_id:
                    # Complex Node subscribe to sender
                    sender = card.get_sender("interface")
                    node.subscribe(sender, node.node_id, dynamic=True, mark_bound=False)
            # Compact the storage
            for node in nodes.values():
                if node.bound_inputs:
                    # Filter Probe nodes
                    node.freeze()
                # Add alarms nodes for clear alarm on delete
                if node.name == "alarm":
                    card.alarms += [node]
            #
            card.affected_rules.add(sys.intern(rule_id))
        card.is_dirty = False
        # Add complex probe
        for cp_metric_filed in source.composed_metrics:
            cp = self.add_probe(cp_metric_filed, k, is_composed=True)
            # Add probe
            for m_field in self.compose_inputs[cp_metric_filed]:
                if m_field in card.probes:
                    card.probes[m_field].subscribe(cp, m_field, dynamic=True, mark_bound=False)
                else:
                    p = self.add_probe(m_field, k)
                    p.subscribe(cp, m_field, dynamic=True, mark_bound=False)
            self.logger.debug("Add compose node: %s", cp)

    def activate_card(
        self, card: Card, si: ScopeInfo, k: MetricKey, data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Activate card and return changed state
        """
        units: Dict[str, str] = data.get("_units") or {}
        tx = self.graph.begin()
        ts = data["ts"]
        for n in data:
            mu = units.get(n) or si.units.get(n)
            if not mu:
                continue  # Missed field
            probe = card.probes.get(n)
            if self.lazy_init and not probe:
                probe = self.add_probe(n, k)
            if not probe or probe.name == ComposeProbeNode.name:  # Skip composed probe
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
            if si.enable_timedelta and "time_delta" in data:
                sender.activate(tx, "time_delta", data["time_delta"])
            sender.activate(tx, "ts", ts)
            sender.activate(tx, "labels", data.get("labels") or [])
        return tx.get_changed_state()

    @staticmethod
    def get_source_config(data):
        sc = SourceConfig(
            type=data["type"],
            bi_id=data["bi_id"],
            fm_pool=data["fm_pool"] if data["fm_pool"] else None,
            labels=tuple(sys.intern(ll["label"]) for ll in data["labels"]),
            metrics=tuple(
                sys.intern(m["name"]) for m in data["metrics"] if not m.get("is_composed")
            ),
            items=[],
        )
        for item in data.get("items", []):
            sc.items.append(
                ItemConfig(
                    key_labels=tuple(sys.intern(ll) for ll in item["key_labels"]),
                    metric_labels=tuple(),
                    metrics=tuple(
                        sys.intern(m["name"]) for m in item["metrics"] if not m.get("is_composed")
                    ),
                    composed_metrics=tuple(
                        sys.intern(m["name"]) for m in item["metrics"] if m.get("is_composed")
                    ),
                )
            )
        return sc

    async def update_source_config(self, data: Dict[str, Any]) -> None:
        """
        Update source config.
        """
        if not self.cards:
            # Initial config
            return
        sc_id = int(data["id"])
        if "type" not in data:
            self.logger.info("[%s] Bad Source data", sc_id)
            return
        sc = self.get_source_config(data)
        self.invalidate_card_config(sc)
        # if sc_id not in self.sources_config:
        #     self.sources_config[sc_id] = sc
        #     return
        # diff = self.sources_config[sc_id].is_differ(sc)
        # if "condition" in diff:
        #    self.invalidate_card_config(sc)

    async def delete_source_config(self, c_id: int) -> None:
        """
        Delete cards for source
        """
        c_id = int(c_id)
        key_ctx = None
        for source_type in ["managed_object", "sla_probe", "sensor", "agent"]:
            key_ctx = (source_type, c_id)
            if key_ctx in self.source_metrics:
                break
        if not key_ctx:
            return
        self.logger.info("Delete cards for source: %s", key_ctx)
        for mk in self.source_metrics[key_ctx]:
            if mk not in self.cards:
                continue
            card = self.cards.pop(mk)
            for a in card.alarms:
                a.reset_state()
            del card
        del self.source_metrics[key_ctx]

    async def on_mappings_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.mappings_ready_event.set()
        self.logger.info("%d SourceConfigs has been loaded", len(self.sources_config))

    def iter_cards(self, sc: SourceConfig) -> Iterable[Card]:
        """
        Iter cards matched source config
        :param sc: Source Config for filter
        :return:
        """
        # Generate context
        if (sc.type, sc.bi_id) not in self.source_metrics:
            return
        # Filter card by key labels
        for mk in self.source_metrics[(sc.type, sc.bi_id)]:
            self.logger.info("[%s] Found Card", mk)
            yield self.cards[mk]

    def invalidate_card_config(self, sc: SourceConfig, delete: bool = False):
        """
        Invalidate Cards on config
        :param sc:
        :param delete: Remove Card
        :return:
        """
        num = 0
        for card in self.iter_cards(sc):
            # Invalidate all card otherwise check rules condition need labels from metrics
            if card.affected_rules:
                card.invalidate_card()
                card.affected_rules = set()
            else:
                card.set_dirty()
            # Check alarm
            for a in card.alarms:
                if delete:
                    a.reset_state()
                    continue
                if a.config.pool != sc.fm_pool:
                    # Hack for ConfigProxy use
                    a.config.__static["pool"] = sc.fm_pool
                    # Alarm config update
            num += 1
        if num:
            self.logger.info("Invalidate %s cards config", num)

    async def invalidate_card_rules(
        self, rules: Iterable[str], is_delete: bool = False, is_new: bool = False
    ):
        """
        Invalidate Cards on rules by identifiers
        :param rules: List that invalidate rule
        :param is_delete: Invalidate for remove rule (reset alarm node)
        :param is_new: Invalidate for new rule (invalidate all nodes)
        :return:
        """
        rules = set(rules)
        self.logger.info("Invalidate card for rules: %s", ";".join(rules))
        num = 0
        for c in self.cards.values():
            if is_new:
                c.set_dirty()
                num += 1
                continue
            if c.affected_rules and c.affected_rules.intersection(rules):
                c.invalidate_card()
                c.affected_rules = set()
                # c.affected_rules -= rules
                num += 1
                if is_delete:
                    while c.alarms:
                        node = c.alarms.pop()
                        await self.change_log.feed({node.node_id: None})
                        del node
        self.logger.info("Invalidate %s cards", num)

    async def update_rules(self, data: Dict[str, Any]) -> None:
        """
        Apply Metric Rules change
        :param data:
        :return:
        """
        invalidate_rules = set()
        for action in data["actions"]:
            rule_id = f'{data["id"]}-{action["id"]}'  # Rule id - join rule and action
            graph = CDAG(f'{data["name"]}-{action["name"]}')
            g_config = GraphConfig(**action["graph_config"])
            scopes = set()
            for a_input in action["inputs"]:
                scopes.add(a_input["sender_id"])
                graph.add_node(
                    f'{rule_id}::{a_input["probe_id"]}',
                    node_type="probe",
                    config={"unit": "1"},
                    sticky=True,
                )
            f = ConfigCDAGFactory(graph, g_config, namespace=rule_id)
            f.construct()
            configs = {}
            for node in g_config.nodes:
                if node.name == "probe" or not node.config:
                    continue
                if node.name == "alarm" and "vars" in node.config:
                    node.config["vars"] = [VarItem(**v) for v in node.config["vars"]]
                configs[f"{rule_id}::{node.name}"] = node.config
            r = Rule(
                id=rule_id,
                match_labels=frozenset(
                    frozenset(sys.intern(label) for label in d["labels"]) for d in data["match"]
                ),
                exclude_labels=None,
                match_scopes=scopes,
                graph=graph,
                configs=configs,
            )
            r_id = sys.intern(r.id)
            if r_id not in self.rules:
                self.rules[r_id] = r
                # For new Rules (after card create)
                self.logger.info("[%s] Add new rule", r.id)
                await self.invalidate_card_rules(invalidate_rules, is_new=True)
                continue
            diff = self.rules[r_id].is_differ(r)
            if diff == {"configs"}:
                # Config only update
                uc = self.rules[r_id].update_config(r.configs)
                self.logger.info("[%s] Update node configs: %s", r.id, uc)
            elif diff.intersection({"conditions", "graph"}):
                # Invalidate Cards
                self.logger.info("[%s] %s Changed. Invalidate cards for rules", r.id, diff)
                self.rules[r_id] = r
                invalidate_rules.add(r_id)
        if invalidate_rules:
            await self.invalidate_card_rules(invalidate_rules)

    async def delete_rules(self, r_id: str) -> None:
        """
        Remove rules for ID
        :param r_id: RuleID
        :return:
        """
        invalidate_rules = set()
        for r in self.rules:
            if r.startswith(r_id):
                invalidate_rules.add(r)
        self.logger.info("[%s] Delete rules: %s", r_id, invalidate_rules)
        if invalidate_rules:
            await self.invalidate_card_rules(invalidate_rules, is_delete=True)
        for r in invalidate_rules:
            del self.rules[r]

    async def on_rules_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.rules_ready_event.set()
        self.logger.info("%d Metric Rules has been loaded", len(self.rules))


if __name__ == "__main__":
    MetricsService().start()
