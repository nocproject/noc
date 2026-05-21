# ----------------------------------------------------------------------
# Metrics card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Set, Iterable, Union, Any
from typing_extensions import TypedDict, NotRequired

# NOC modules
from noc.core.perf import metrics
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.probe import ProbeNode, ProbeNodeConfig
from noc.core.cdag.node.metrics import MetricsNode
from noc.core.cdag.node.alarm import AlarmNode
from noc.core.cdag.node.composeprobe import ComposeProbeNode
from noc.core.cdag.node.threshold import ThresholdNode
from .target import MetricKey, ManagedObjectTarget, SLAProbeTarget
from .rule import Rule


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
        "config",
        "is_dirty",
        "probes",
        "composed",
        "senders",
        "last_touch",
    )
    probes: Dict[Tuple[str, str], ProbeNode]
    composed: Tuple[ComposeProbeNode]
    senders: Tuple[MetricsNode, ...]
    alarms: List[Union[ThresholdNode, AlarmNode]]
    affected_rules: Set[str]
    config: Optional[Union[ManagedObjectTarget, SLAProbeTarget]]
    is_dirty: bool
    last_touch: Optional[int]

    @classmethod
    def iter_subscribed_nodes(cls, node) -> Iterable[BaseCDAGNode]:
        """Iterate over nodes subscribed to Probes on Card"""
        for s in node.iter_subscribers():
            yield s.node
            yield from cls.iter_subscribed_nodes(s.node)

    def add_probe(self, k: MetricKey, probe: ProbeNode):
        """Add probe"""
        if probe.name == "composeprobe":
            self.composed = tuple([*list(self.composed or []), probe])
        else:
            self.probes[(k, unscope(probe.node_id))] = probe

    def get_probe(self, k: MetricKey, probe: str) -> Optional[ProbeNode]:
        """Request metric probe"""
        if (k, probe) in self.probes:
            return self.probes[k, probe]
        return None

    def get_sender(self, name: str) -> Optional[MetricsNode]:
        """Get probe sender by name"""
        return next((s for s in self.senders if s.config.scope == name), None)

    def iter_senders(self, name: str):
        for s in self.senders:
            if s.config.scope == name:
                yield s

    def clone_and_add_node(
        self,
        n: BaseCDAGNode,
        prefix: str,
        config: Optional[Dict[str, Any]] = None,
        static_config=None,
        state=None,
    ) -> BaseCDAGNode:
        """
        Clone node without subscribers and apply state and config
        """
        # state_id = f"{prefix}::{n.node_id}"
        # state = self.start_state.pop(state_id, None)
        new_node = n.clone(
            n.node_id, prefix=prefix, state=state, config=config, static_config=static_config
        )
        # metrics["cdag_nodes", ("type", n.name)] += 1
        return new_node

    def add_cdag(self, name, src, prefix=None):
        nodes = {}
        for node in src.nodes.values():
            # Apply sender nodes
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
        self.senders = tuple(list(self.senders or []) + [node for node in nodes.values() if node.name == "metrics"])

    def apply_rule(self, rule: Rule):
        """Apply Metric Rule to card"""

    def touch(self, ts: int):
        """"""
        self.last_touch = ts

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
        #if not self.component:
        #    return self.config.rules or []
        return self.config.rules or []

    @property
    def composed_metrics(self):
        # if not self.component:
        #     return self.config.composed_metrics or []
        return self.config.composed_metrics or []

    def get_probe_config(self) -> ProbeNodeConfig:
        """"""
        if self.component and hasattr(self.component, "units"):
            return ProbeNodeConfig(unit=self.component.units or "1")
        return None
