# ----------------------------------------------------------------------
# Metrics Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, FrozenSet

# NOC modules
from noc.core.cdag.graph import CDAG


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
        if not self.match_labels and not self.exclude_labels:
            return True
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
