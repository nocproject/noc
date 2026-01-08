#!./bin/python
# ----------------------------------------------------------------------
# Metrics service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Any, Dict, Tuple, List, Optional, Set, Iterable, Union
import sys
import asyncio
import codecs
import hashlib

# Third-party modules
import orjson
import cachetools

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.mongo.connection_async import connect_async
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.probe import ProbeNode, ProbeNodeConfig
from noc.core.cdag.node.composeprobe import ComposeProbeNode, ComposeProbeNodeConfig
from noc.core.cdag.node.alarm import VarItem
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.scope import MetricScopeCDAGFactory
from noc.core.cdag.factory.config import ConfigCDAGFactory, GraphConfig
from noc.services.metrics.changelog import ChangeLog
from noc.services.metrics.datastream import MetricsDataStreamClient, MetricRulesDataStreamClient
from noc.services.metrics.models.card import Card, ScopeInfo
from noc.services.metrics.models.rule import Rule
from noc.services.metrics.models.target import (
    MetricKey,
    MetricTarget,
    ManagedObjectTarget,
    SLAProbeTarget,
    SensorTarget,
    ComponentTarget,
)
from noc.config import config as global_config

# MetricKey - scope, key ctx: (managed_object, <bi_id>), Key Labels
ObjectTarget = Union[ManagedObjectTarget, SLAProbeTarget]


def unscope(x):
    return sys.intern(x.rsplit("::", 1)[-1])


class MetricsService(FastAPIService):
    name = "metrics"
    use_mongo = True
    use_router = True
    dcs_check_interval = global_config.metrics.check_interval
    dcs_check_timeout = global_config.metrics.check_timeout

    def __init__(self):
        super().__init__()
        # Metric Configs
        self.scopes: Dict[str, ScopeInfo] = {}
        self.metric_configs: Dict[
            Tuple[str, str], Union[ProbeNodeConfig, ComposeProbeNodeConfig]
        ] = {}
        self.compose_inputs: Dict[str, Set] = {}
        self.scope_cdag: Dict[str, CDAG] = {}  # Scope graph cache
        self.cards: Dict[MetricKey, Card] = {}  # Metric cards
        self.graph: Optional[CDAG] = None  # Service Metric Graph
        # Graph node State
        self.change_log: Optional[ChangeLog] = None
        self.start_state: Dict[str, Dict[str, Any]] = {}
        # Source Configs
        self.targets: Dict[int, ObjectTarget] = {}
        self.sensors: Dict[int, SensorTarget] = {}
        self.dispose_partitions: Dict[str, int] = {}
        self.rules: Dict[str, Rule] = {}  # Action -> Graph Config
        # Options
        self.lazy_init: bool = True  # Load Nodes on processed metrics
        self.disable_spool: bool = (
            global_config.metrics.disable_spool
        )  # Disable Send metric record to Clickhouse
        self.target_card_map: Dict[int, List[MetricKey]] = defaultdict(list)
        # Sync primitives
        self.mappings_ready_event = asyncio.Event()  # Load Metric Sources
        self.rules_ready_event = asyncio.Event()  # Load Metric Rules
        self.sync_cursor_condition: Optional[asyncio.Condition] = (
            None  # Condition for commit stream cursor
        )

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        self.change_log = ChangeLog(self.slot_number)
        connect_async()
        self.load_scopes()
        self.start_state = await self.change_log.get_state()
        self.graph = CDAG("metrics")
        if global_config.metrics.flush_interval > 0:
            asyncio.create_task(self.log_runner())
        # Start tracking changes
        asyncio.get_running_loop().create_task(self.get_metric_rules_mappings())
        asyncio.get_running_loop().create_task(self.get_object_mappings())
        # Subscribe metrics stream
        asyncio.get_running_loop().create_task(self.subscribe_metrics())

    async def subscribe_metrics(self) -> None:
        self.logger.info("Waiting for rules")
        await self.rules_ready_event.wait()
        self.logger.info("Waiting for mappings")
        await self.mappings_ready_event.wait()
        self.logger.info("Mappings are ready")
        await self.subscribe_stream(
            "metrics",
            self.slot_number,
            self.on_metrics,
            async_cursor_condition=self.sync_cursor_condition,
        )

    async def on_deactivate(self):
        if self.change_log:
            await self.change_log.flush()
            async with self.sync_cursor_condition:
                self.sync_cursor_condition.notify_all()
            self.change_log = None

    async def log_runner(self):
        self.logger.info("Run log runner")
        self.sync_cursor_condition = asyncio.Condition()
        while True:
            await asyncio.sleep(global_config.metrics.flush_interval)
            if self.change_log:
                await self.change_log.flush()
                async with self.sync_cursor_condition:
                    self.sync_cursor_condition.notify_all()

    async def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = MetricsDataStreamClient("cfgmetricstarget", service=self)
        # coll = CfgMetricSourcesDataStream.get_collection()
        # r = next(coll.find({}).sort([("change_id", DESCENDING)]), None)
        # Track stream changes
        while True:
            self.logger.info(
                "Starting to track object mappings: %s/%s", self.slot_number, self.total_slots
            )
            try:
                await client.query(
                    limit=global_config.metrics.ds_limit,
                    filters=[f"shard({self.slot_number},{self.total_slots})"],
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
            if si.required_labels and not labels:
                self.logger.debug("No labels: %s", item)
                metrics["discard", ("reason", "no_labels")] += 1
                return  # No labels
            mk, req = self.get_key(si, item)
            if si.required_labels and len(req) != len(si.required_labels):
                self.logger.debug("Missed key label: %s", item)
                metrics["discard", ("reason", "missed_keylabel")] += 1
                return  # Missed key label
            card = await self.get_card(mk, labels)
            if not card:
                self.logger.info("Cannot instantiate card: %s", item)
                return  # Cannot instantiate card
            # Exposed labels
            if card.config and card.config.exposed_labels:
                # Add component labels
                item["labels"] = labels + list(card.config.exposed_labels)
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
                    is_delta=mt.is_delta,
                    expression=mt.compose_expression,
                )
                self.compose_inputs[mt.field_name] = {m_t.field_name for m_t in mt.compose_inputs}
                continue
            self.metric_configs[(mt.scope.table_name, mt.field_name)] = ProbeNodeConfig(
                unit=(mt.units.code or "1") if mt.units else "1",
                is_delta=mt.is_delta,
                scale=mt.scale.code if mt.scale else "1",
            )
        for ms in MetricScope.objects.all():
            self.logger.debug("Loading scope %s", ms.table_name)
            si = ScopeInfo(
                scope=ms.table_name,
                key_fields=tuple(sorted(kf.field_name for kf in ms.key_fields)),
                key_labels=tuple(
                    sorted(kl.label[:-1] for kl in ms.labels if kl.is_required or kl.is_key_label)
                ),
                required_labels=tuple(sorted(kl.label[:-1] for kl in ms.labels if kl.is_required)),
                units=units[ms.id],
                enable_timedelta=ms.enable_timedelta,
            )
            self.scopes[ms.table_name] = si
            self.logger.debug(
                "[%s] key fields: %s, key labels: %s, required labels: %s",
                si.scope,
                si.key_fields,
                si.key_labels,
                si.required_labels,
            )

    @staticmethod
    def get_key(si: ScopeInfo, data: Dict[str, Any]) -> Tuple[MetricKey, Tuple[str, ...]]:
        def iter_labels(f_labels):
            if not labels or not f_labels:
                return
            for k in f_labels:
                v = scopes.get(k)
                if v is not None:
                    yield v

        labels = data.get("labels")
        scopes = {f"{ll.rsplit('::', 1)[0]}::": ll for ll in labels or []}
        return (
            (
                si.scope,
                tuple((k, data[k]) for k in si.key_fields if k in data),
                tuple(iter_labels(si.key_labels)),
            ),
            tuple(iter_labels(si.required_labels)),
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
        if card:
            return card
        # Generate new CDAG
        cdag = self.get_scope_cdag(k)
        if not cdag:
            return None
        target, cp = self.get_target(k)
        # Apply CDAG to a common graph and collect inputs to the card
        card = await self.project_cdag(
            cdag,
            prefix=self.get_key_hash(k),
            config=target,
            component=cp,
        )
        metrics["project_cards"] += 1
        self.cards[k] = card
        if target:
            # Skip metric for sensor
            self.target_card_map[target.bi_id].append(k)
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
            cdag,
            scope=ms,
            sticky=True,
            spool=not self.disable_spool,
            lazy_init=self.lazy_init,
            spool_message=global_config.message.enable_metrics
            and ms.table_name in set(global_config.message.enable_metric_scopes),
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

    async def project_cdag(
        self,
        src: CDAG,
        prefix: str,
        config: Optional[ManagedObjectTarget] = None,
        component: Optional[ComponentTarget] = None,
    ) -> Card:
        """
        Project `src` to a current graph and return the controlling Card
        Args:
            src: Applied graph
            prefix: Unique card prefix
            config:
            component:
        """

        nodes: Dict[str, BaseCDAGNode] = {}
        # Clone nodes
        for node in src.nodes.values():
            # Apply sender nodes
            nodes[node.node_id] = self.clone_and_add_node(
                node,
                prefix=prefix,
                # config=(
                #     {
                #         "message_meta": config.meta or {},
                #         # "message_labels": MX_H_VALUE_SPLITTER.join(config.labels).encode(
                #         #     encoding=DEFAULT_ENCODING
                #         # ),
                #     }
                #     if config
                #     else None
                # ),
            )
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
            config=config,
            component=component,
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
        self, metric_field: str, k: MetricKey, is_composed: bool = False, unit: Optional[str] = None
    ) -> Optional[ProbeNode]:
        """
        Add new probe to card
        Args:
            metric_field: Metric field name
            k: Metric key
            is_composed: Create ComposeProbeNode
            unit: Measurement Unit
        """
        card = self.cards[k]
        mt = MetricType.get_by_field_name(metric_field, k[0])
        if not mt:
            if not is_composed:
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
        cfg = self.metric_configs.get((k[0], metric_field))
        if unit:
            cfg.unit = unit
        # Create Probe
        p = probe_cls.construct(
            metric_field,
            prefix=prefix,
            state=self.start_state.pop(state_id, None),
            config=cfg,
            sticky=True,
        )
        # Subscribe
        p.subscribe(sender, metric_field, dynamic=True, mark_bound=False)
        p.freeze()
        card.probes[unscope(metric_field)] = p
        metrics["cdag_nodes", ("type", p.name)] += 1
        return p

    def get_target(
        self, k: MetricKey
    ) -> Optional[Tuple[Optional[MetricTarget], Optional[ComponentTarget]]]:
        """Resolve metrics target"""
        key_ctx = dict(k[1])
        if key_ctx.get("sensor"):
            tid = key_ctx["sensor"]
            return self.sensors.get(tid), None
        if key_ctx.get("sla_probe"):
            tid = key_ctx["sla_probe"]
        elif key_ctx.get("agent"):
            tid = key_ctx["agent"]
        elif "managed_object" in key_ctx:
            tid = key_ctx["managed_object"]
        else:
            self.logger.info("Not Found Source info")
            return None, None
        target = self.targets.get(tid)
        if not target:
            self.logger.info("[%s] Unknown Source", tid)
            return None, None
        return target, None

    def apply_rules(self, k: MetricKey, labels: List[str]):
        """
        Apply rule Graph
        :param k: Metric key
        :param labels: Metric labels
        :return:
        """
        card = self.cards[k]
        if not card.config or card.is_dirty:
            # Getting Context
            card.config, card.component = self.get_target(k)
        if not card.config:
            self.logger.debug("[%s] Unknown metric source. Skipping apply rules", k)
            metrics["unknown_metric_source"] += 1
            return
        # Replace to card.iter_rules
        target = card.config
        # s_labels = set(self.merge_labels(source.labels, labels))
        # Apply matched rules
        # for rule_id, rule in self.rules.items():
        rules = card.get_rules()
        if rules:
            self.logger.debug("[%s] Apply Rules: %s", k, rules)
        for rule_id, action_id in rules:
            # if k[0] not in rule.match_scopes or not rule.is_matched(s_labels):
            #    continue
            rule_id = f"{rule_id}-{action_id}"
            if rule_id not in self.rules:
                self.logger.debug("[%s] Broken rules", rule_id)
                continue
            rule = self.rules[rule_id]
            if not rule or k[0] not in rule.match_scopes:
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
                if (
                    node.name == "probe"
                    and node_id not in card.probes
                    and "compose_" not in node_id
                ):
                    # Metrics probe is not initialized yet, add_probe. Skip compose  metric node
                    probe = self.add_probe(node_id, k, unit=card.m_unit)
                    nodes[node.node_id] = probe
                    continue
                config = rule.configs.get(node.node_id)
                static_config = None
                if node.name in {"alarm", "threshold"} and target.managed_object:
                    slots = self.get_slot_limits(f"correlator-{target.fm_pool}")
                    static_config = {
                        "managed_object": f"bi_id:{target.managed_object}",
                        "partition": target.bi_id % slots or 0,
                        "pool": target.fm_pool,
                        "labels": k[2],
                    }
                    if target.type == "sla_probe":
                        static_config["sla_probe"] = target.bi_id
                    if target.type == "sensor":
                        static_config["sensor"] = target.bi_id
                    self.logger.debug("Create Alarm Node with config %s", static_config)
                nodes[node.node_id] = self.clone_and_add_node(
                    node, prefix=self.get_key_hash(k), config=config, static_config=static_config
                )
            if (
                f"{rule_id}::alarm" not in nodes
                and f"{rule_id}::threshold" not in nodes
                and f"{rule_id}::probe" not in nodes
            ):
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
                if node.name in {"alarm", "threshold"}:
                    card.alarms += [node]
            card.affected_rules.add(sys.intern(rule_id))
        card.is_dirty = False
        # Add complex probe
        for cp_metric_filed in card.composed_metrics:
            cp = self.add_probe(cp_metric_filed, k, is_composed=True)
            if not cp:
                # Not matched scope
                continue
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
    ) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """
        Activate card and return changed state
        """
        units: Dict[str, str] = data.get("_units") or {}
        tx = self.graph.begin()
        ts = data["ts"]
        time_delta = None
        for n in data:
            mu = units.get(n) or si.units.get(n)
            if not mu:
                continue  # Missed field
            probe = card.probes.get(n)
            if self.lazy_init and not probe:
                probe = self.add_probe(n, k, unit=card.m_unit)
            if not probe:
                continue
            if probe.name == ComposeProbeNode.name:  # Skip composed probe
                probe.activate(tx, "time_delta", time_delta)
                continue
            if time_delta is None:
                time_delta = probe.get_time_delta(ts)
            probe.activate(tx, "ts", ts)
            probe.activate(tx, "x", data[n])
            probe.activate(tx, "unit", mu)
        # Activate senders
        for sender in card.senders:
            for kf in si.key_fields:
                kv = data.get(kf)
                if kv is not None:
                    sender.activate(tx, kf, kv)
            if si.enable_timedelta and time_delta:
                sender.activate(tx, "time_delta", time_delta)
            sender.activate(tx, "target", card.config)
            sender.activate(tx, "ts", ts)
            sender.activate(tx, "labels", data.get("labels") or [])
        return tx.get_changed_state()

    def update_sensors(self, target: ObjectTarget, sensors: List[Dict[str, Any]]):
        """Update sensors info"""
        if target.type != "managed_object":
            return
        processed = set()
        for d in sensors:
            sensor = MetricTarget.from_config(d, "sensor")
            if not sensor:
                continue
            self.sensors[sensor.bi_id] = sensor
            processed.add(sensor.bi_id)
        # Remove Unused sensors
        for sid in target.sensors - processed:
            if sid not in self.sensors:
                continue
            sensor = self.sensors.pop(sid)
            self.logger.info("[%s] Remove sensor: %s", target, sensor)

    async def update_source_config(self, data: Dict[str, Any]) -> None:
        """
        Update source config.
        """
        # if not self.cards:
        #     # Initial config
        #     return
        if "type" not in data:
            self.logger.info("[%s] Bad Source data", data["id"])
            return
        target = MetricTarget.from_config(data, data["type"])
        if not target:
            # Unknown target type
            return
        tid = int(target.bi_id)
        if tid not in self.targets:
            # New
            self.targets[tid] = target
            self.update_sensors(target, data.get("sensors", []))
            return
        # Apply Sensors
        self.update_sensors(self.targets[tid], data.get("sensors", []))
        # Check Changed
        if target == self.targets[tid]:
            self.logger.info("Source config is same. Continue")
            return
        # Invalidate Cards
        self.targets[tid] = target
        self.invalidate_card_config(target)
        # diff = self.sources_config[sc_id].is_differ(sc)
        # if "condition" in diff:
        #    self.invalidate_card_config(sc)

    async def delete_source_config(self, c_id: int) -> None:
        """
        Delete cards for source
        """
        c_id = int(c_id)
        if c_id not in self.targets:
            self.logger.debug("[%s] Unknown target for remove", c_id)
            return
        self.logger.info("Delete cards for source: %s", c_id)
        for mk in self.target_card_map[c_id]:
            if mk not in self.cards:
                continue
            card = self.cards.pop(mk)
            for a in card.alarms:
                a.reset_state()
            del card
        del self.targets[c_id]

    async def on_mappings_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.mappings_ready_event.set()
        self.logger.info("%d Targets has been loaded", len(self.targets))
        self.logger.info("%d Sensors has been loaded", len(self.sensors))

    def iter_cards(self, target: MetricTarget) -> Iterable[Card]:
        """Iter cards matched source config"""
        # Generate context
        if target.bi_id not in self.target_card_map:
            return
        # Filter card by key labels
        for mk in self.target_card_map[target.bi_id]:
            self.logger.info("[%s] Found Card", mk)
            yield self.cards[mk]

    def invalidate_card_config(self, sc: MetricTarget, delete: bool = False):
        """Invalidate Cards on config"""
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
        """Apply Metric Rules change"""
        # Add Invalidate Graph
        invalidate_rules = set()
        for action in data["actions"]:
            rule_id = f"{data['id']}-{action['id']}"  # Rule id - join rule and action
            graph = CDAG(f"{data['name']}-{action['name']}")
            g_config = GraphConfig(**action["graph_config"])
            scopes = set()
            for a_input in action["inputs"]:
                scopes.add(a_input["sender_id"])
                graph.add_node(
                    f"{rule_id}::{a_input['probe_id']}",
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
                if node.name in {"alarm", "threshold"} and "vars" in node.config:
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
