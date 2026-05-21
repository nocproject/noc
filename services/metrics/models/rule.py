# ----------------------------------------------------------------------
# Metrics Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, FrozenSet, List

# NOC modules
from noc.services.datastream.models.cfgmetricrules import RuleAction, RuleCondition
from noc.core.cdag.graph import CDAG
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.node.alarm import VarItem
from noc.core.cdag.factory.config import ConfigCDAGFactory
from noc.core.perf import metrics


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
    # probes - inputs
    # is_delete: bool
    # alarms,composed,intergraph (send state) - outputs

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
        metrics["rule_nodes", ("type", n.name)] += 1
        return new_node

    @classmethod
    def from_config(
        cls,
        rule_id: str,
        action: RuleAction,
        rule_name: str,
        conditions: List[RuleCondition],
    ) -> "Rule":
        """Build rule from config"""
        rule_id = f"{rule_id}-{action.id}"
        graph = CDAG(f"{rule_name}-{action.name}")
        scopes = set()
        for a_input in action.inputs:
            scopes.add(a_input.sender_id)
            graph.add_node(
                f"{rule_id}::{a_input.probe_id}",
                node_type="probe",
                config={"unit": "1"},
                sticky=True,
            )
        f = ConfigCDAGFactory(graph, action.graph_config, namespace=rule_id)
        f.construct()
        configs = {}
        for node in action.graph_config.nodes:
            if node.name == "probe" or not node.config:
                continue
            if node.name in {"alarm", "threshold"} and "vars" in node.config:
                node.config["vars"] = [VarItem(**v) for v in node.config["vars"]]
            configs[f"{rule_id}::{node.name}"] = node.config
        return Rule(
            id=rule_id,
            match_labels=frozenset(
                frozenset(sys.intern(label) for label in c.labels) for c in conditions
            ),
            exclude_labels=None,
            match_scopes=scopes,
            graph=graph,
            configs=configs,
        )
