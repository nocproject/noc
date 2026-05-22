# ----------------------------------------------------------------------
# Metrics card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Set, Iterable, Union
from typing_extensions import TypedDict, NotRequired

# NOC modules
from noc.core.perf import metrics
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.probe import ProbeNode, ProbeNodeConfig
from noc.core.cdag.node.metrics import MetricsNode
from noc.core.cdag.node.alarm import AlarmNode
from noc.core.cdag.node.threshold import ThresholdNode
from .target import ManagedObjectTarget, ComponentTarget, SensorComponentTarget
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

    __slots__ = ("affected_rules", "alarms", "component", "config", "is_dirty", "probes", "senders")
    probes: Dict[str, ProbeNode]
    senders: Tuple[MetricsNode, ...]
    alarms: List[Union[ThresholdNode, AlarmNode]]
    affected_rules: Set[str]
    config: Optional[Union[ManagedObjectTarget, SensorComponentTarget]]
    component: Optional[ComponentTarget]
    is_dirty: bool

    def get_sender(self, name: str) -> Optional[MetricsNode]:
        """Get probe sender by name"""
        return next((s for s in self.senders if s.config.scope == name), None)

    def apply_rule(self, rule: Rule):
        """Apply Metric Rule to card"""

    def get_probe(self, metric: str) -> Optional[ProbeNode]:
        return self.probes.get(metric)

    def add_probe(self, metric_field: str, probe: ProbeNode):
        self.probes[unscope(metric_field)] = probe

    @classmethod
    def iter_subscribed_nodes(cls, node) -> Iterable[BaseCDAGNode]:
        """
        Iterate over nodes subscribed to Probes on Card
        """
        for s in node.iter_subscribers():
            yield s.node
            yield from cls.iter_subscribed_nodes(s.node)

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
    def composed_metrics(self):
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
