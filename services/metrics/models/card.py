# ----------------------------------------------------------------------
# Metrics card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Set, Iterable

# NOC modules
from noc.core.perf import metrics
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.alarm import AlarmNode
from .source import SourceInfo


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str, ...]
    key_labels: Tuple[str, ...]
    required_labels: Tuple[str, ...]
    units: Dict[str, str]
    enable_timedelta: bool = False


@dataclass
class Card(object):
    """
    Store Input probe nodes
    """

    __slots__ = ("alarms", "probes", "senders", "is_dirty", "affected_rules", "config")
    probes: Dict[str, BaseCDAGNode]
    senders: Tuple[BaseCDAGNode, ...]
    alarms: List[AlarmNode]
    affected_rules: Set[str]
    config: Optional[SourceInfo]
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
