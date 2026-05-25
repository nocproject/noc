# ----------------------------------------------------------------------
# Metrics card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import logging
import hashlib
import codecs
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Set, Iterable, Union, Any, ClassVar, FrozenSet
from typing_extensions import TypedDict, NotRequired

# Third-party modules
import cachetools

# NOC modules
from noc.core.perf import metrics
from noc.core.cdag.graph import CDAG
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.probe import ProbeNode, ProbeNodeConfig
from noc.core.cdag.node.composeprobe import ComposeProbeNode
from noc.core.cdag.node.metrics import MetricsNode
from noc.core.cdag.node.alarm import AlarmNode
from noc.core.cdag.node.threshold import ThresholdNode
from noc.core.cdag.factory.config import ConfigCDAGFactory
from noc.pm.models.metrictype import MetricType
from .target import (
    MetricKey,
    ManagedObjectTarget,
    ComponentTarget,
    SLAProbeTarget,
    SensorComponentTarget,
)
from .rule import Rule


logger = logging.getLogger(__name__)


def unscope(x):
    return sys.intern(x.rsplit("::", 1)[-1])


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str, ...]
    key_labels: Tuple[str, ...]
    required_labels: Tuple[str, ...]
    units: Dict[str, str]
    enable_timedelta: bool = False


class MetricsItem(TypedDict, closed=True):
    scope: str
    ts: int
    labels: List[str]
    managed_object: int
    sla_probe: NotRequired[int]
    agent: NotRequired[int]
    service: NotRequired[int]
    sensor: NotRequired[int]
    _units: Dict[str, str]
    # Any key other than 'title' or 'year' must have a boolean value
    __extra_items__: float


@dataclass
class Card(object):
    """
    Store Input probe nodes
    """

    __slots__ = (
        "affected_rules",
        "alarms",
        "component",
        "config",
        "graphs",
        "is_dirty",
        "probes",
        "senders",
    )
    init_state: ClassVar[Dict[str, Dict[str, Any]]] = {}
    compose_node_inputs: ClassVar[Dict[str, Set[str]]] = {}

    probes: Dict[str, ProbeNode]
    senders: Tuple[MetricsNode, ...]
    alarms: List[Union[ThresholdNode, AlarmNode]]
    affected_rules: FrozenSet[str]
    graphs: Dict[str, CDAG]
    config: Optional[Union[ManagedObjectTarget, SLAProbeTarget]]
    component: Optional[Union[ComponentTarget, SensorComponentTarget]]
    is_dirty: bool

    def get_sender(self, name: str) -> Optional[MetricsNode]:
        """Get probe sender by name"""
        return next((s for s in self.senders if s.config.scope == name), None)

    def get_probe(self, metric: str) -> Optional[ProbeNode]:
        return self.probes.get(metric)

    def add_probe(self, metric_field: str, probe: ProbeNode):
        self.probes[unscope(metric_field)] = probe

    @staticmethod
    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60))
    def get_key_hash(k: MetricKey) -> str:
        """
        Calculate persistent hash for metric key
        """
        d = hashlib.blake2b(str(k).encode("utf-8")).digest()
        return codecs.encode(d, "base_64")[:7].decode("utf-8")

    @classmethod
    def iter_subscribed_nodes(cls, node) -> Iterable[BaseCDAGNode]:
        """
        Iterate over nodes subscribed to Probes on Card
        """
        for s in node.iter_subscribers():
            yield s.node
            yield from cls.iter_subscribed_nodes(s.node)

    @classmethod
    def clone_and_add_node(
        cls,
        n: BaseCDAGNode,
        prefix: str,
        config: Optional[Dict[str, Any]] = None,
        static_config=None,
    ) -> BaseCDAGNode:
        """
        Clone node without subscribers and apply state and config
        """
        state_id = f"{prefix}::{n.node_id}"
        state = cls.init_state.pop(state_id, None)
        new_node = n.clone(
            n.node_id, prefix=prefix, state=state, config=config, static_config=static_config
        )
        metrics["cdag_nodes", ("type", n.name)] += 1
        return new_node

    @classmethod
    def from_graph(
        cls,
        src: CDAG,
        prefix: str,
        config: Optional[ManagedObjectTarget] = None,
        component: Optional[ComponentTarget] = None,
    ):
        nodes: Dict[str, BaseCDAGNode] = {}
        # Clone nodes
        for node in src.nodes.values():
            # Apply sender nodes
            nodes[node.node_id] = cls.clone_and_add_node(node, prefix=prefix)
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
            graphs={},
            affected_rules=set(),
            is_dirty=False,
            config=config,
            component=component,
        )

    def add_node_probe(
        self,
        metric_field: str,
        k: MetricKey,
        is_composed: bool = False,
        cfg: Optional[ProbeNodeConfig] = None,
    ) -> Optional[ProbeNode]:
        """
        Add new probe to card
        Args:
            metric_field: Metric field name
            k: Metric key
            is_composed: Create ComposeProbeNode
            unit: Measurement Unit
        """
        mt = MetricType.get_by_field_name(metric_field, k[0])
        if not mt:
            if not is_composed:
                logger.warning("[%s] Unknown metric field: %s", k, metric_field)
            return None
        sender = self.get_sender(mt.scope.table_name)
        if not sender:
            logger.debug("[%s] Sender is not found on Card: %s", k, mt.scope.table_name)
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
            state=self.init_state.pop(state_id, None),
            config=cfg or mt.probe_config,
            sticky=True,
        )
        if not p:
            return None
        # Subscribe
        p.subscribe(sender, metric_field, dynamic=True, mark_bound=False)
        p.freeze()
        self.add_probe(metric_field, p)
        metrics["cdag_nodes", ("type", p.name)] += 1
        return p

    def add_compose_probe(self, metric_field: str, k: MetricKey):
        """Add composed node probe"""
        cp = self.add_node_probe(metric_field, k, is_composed=True)
        if not cp:
            # Not matched scope
            return
        # Add probe
        for m_field in self.compose_node_inputs[metric_field]:
            p = self.get_probe(m_field)
            cp.add_input(m_field, is_key=True)
            if not p:
                p = self.add_node_probe(m_field, k)
            if p:
                p.subscribe(cp, m_field, dynamic=True, mark_bound=False)
        logger.debug("Add compose node: %s", cp)

    def invalidate_card(self):
        """Remove all subscribed node and set  is_dirty for applied rules"""
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

    def invalidate_alarms(self, remove_all: bool = False) -> List[Tuple[str, str]]:
        """Remove not affected alarms node and return node_id"""
        r = []
        # Actual rules
        rules = {f"{rule_id}-{action_id}" for rule_id, action_id in self.get_rules()}
        if remove_all:
            to_deleted = self.affected_rules
        else:
            to_deleted = self.affected_rules - rules
        if not to_deleted:
            return []
        alarms = []
        # Unsubscribe
        for a in self.alarms:
            if a.rule_id not in to_deleted:
                alarms.append(a)
            else:
                r.append((a.node_id, a.name))
                del a
        self.alarms = alarms
        if r:
            self.set_dirty()
        return r

    def set_dirty(self):
        self.is_dirty = True

    def get_rules(self) -> Iterable[Tuple[str, str]]:
        """Get metric rules"""
        if self.component:
            return self.component.rules or []
        if self.config:
            return self.config.rules or []
        return []

    @property
    def composed_metrics(self) -> List[str]:
        if self.component:
            return self.component.composed_metrics or []
        if self.config:
            return self.config.composed_metrics or []
        return []

    def get_probe_config(self) -> ProbeNodeConfig:
        """"""
        if self.component and hasattr(self.component, "units"):
            return ProbeNodeConfig(unit=self.component.units or "1")
        return None

    def apply_rule(self, rule: Rule, k: MetricKey):
        """"""
        namespace = self.get_key_hash(k)
        graph = CDAG(f"{namespace}::{rule.id}", state=self.init_state)
        graph.nodes |= {f"{namespace}::{k}": v for k, v in self.probes.items()}
        # graph.add_node(
        #   f"{rule_id}::{a_input.probe_id}",
        #    node_type="probe",
        #    config={"unit": "1"},
        #    sticky=True,
        # )
        f = ConfigCDAGFactory(
            graph,
            rule.graph_config,
            namespace=namespace,
            nodes_config=rule.configs,
            node_config_prefix=rule.id,
        )
        f.construct()
        self.graphs[graph.graph_id] = graph
        if f"{namespace}::alarm" in graph.nodes:
            self.alarms = [graph.nodes[f"{namespace}::alarm"]]
        self.affected_rules.add(sys.intern(rule.id))

    def refresh_card(
        self,
        k: MetricKey,
        labels: List[str],
        rules: Dict[str, Rule],
    ):
        """Refresh card. Update composed, Refresh Graph"""
        # Composed nodel
        if not self.config:
            logger.debug("[%s] Unknown metric source. Skipping apply rules", k)
            metrics["unknown_metric_source"] += 1
            return
        for c in set(self.composed_metrics) - self.probes.keys():
            self.add_compose_probe(c, k)
        # Refresh Rule
        processed, scopes = set(), set()
        config_rules = self.get_rules()
        for rule_id, action_id in config_rules:
            # if k[0] not in rule.match_scopes or not rule.is_matched(s_labels):
            #    continue
            rid = f"{rule_id}-{action_id}"
            if rid not in rules:
                logger.warning("[%s] Broken rules", rid)
                continue
            processed.add(rid)
            if rid in self.graphs:
                # Already applied
                continue
            rule = rules[rid]
            if not rule or k[0] not in rule.match_scopes:
                continue
            if rule.inputs - self.probes.keys():
                logger.info("Not activated probes: %s", rule.inputs)
                self.set_dirty()
                continue
            scopes.add(k[0])
            self.apply_rule(rule, k)
            # Register composed and Alarm
        # Removed
        for rule_id in self.graphs.keys() - processed:
            graph = self.graphs.pop(rule_id, None)
            del graph
        if processed and scopes:
            logger.info("[%s] Apply Rules: %s; To scopes: %s", k, processed, scopes)
        if config_rules and not scopes:
            return
        self.is_dirty = False
