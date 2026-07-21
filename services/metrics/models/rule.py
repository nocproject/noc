# ----------------------------------------------------------------------
# Metrics Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from dataclasses import dataclass
from typing import Any

# NOC modules
from noc.services.datastream.models.cfgmetricrules import RuleAction, RuleCondition
from noc.core.cdag.graph import CDAG
from noc.core.cdag.node.alarm import AlarmNode
from noc.core.cdag.factory.config import ConfigCDAGFactory, GraphConfig


@dataclass
class Rule:
    """
    Store Rule actions, configs and conditions
    """

    id: str
    match_labels: frozenset[frozenset[str]]
    exclude_labels: frozenset[frozenset[str]] | None
    graph_config: GraphConfig
    match_scopes: set[str]
    inputs: set[str]
    configs: dict[str, dict[str, Any]]  # NodeId -> Config
    alarms: tuple[AlarmNode]
    # is_delete: bool
    # alarms,composed,intergraph (send state) - outputs

    def is_matched(self, labels: set[str]) -> bool:
        if not self.match_labels and not self.exclude_labels:
            return True
        return any(labels.issuperset(ml) for ml in self.match_labels)

    def is_differ(self, rule: "Rule") -> frozenset[str]:
        """
        Diff nodes config - update configs only
        Diff graph nodes or structure - rebuld Card Rules
        Diff condition - rebuild or remove Card Rules
        :return:
        """
        r = []
        if {n.name for n in self.graph_config.nodes} != {n.name for n in rule.graph_config.nodes}:
            # If compare Graph Node config always diff if change
            r.append("graph")
        if self.match_labels != rule.match_labels:
            r.append("conditions")
        if self.configs != rule.configs:
            r.append("configs")
        return frozenset(r)

    def update_config(self, configs: dict[str, dict[str, Any]]) -> set[str]:
        """
        Update node config, return changed node
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

    def build_graph(self, inputs: list[str], namespace: str, states=None) -> CDAG:
        graph = CDAG(f"{namespace}::{self.id}", state=states)
        f = ConfigCDAGFactory(
            graph,
            self.graph_config,
            namespace=namespace,
            nodes_config=self.configs,
        )
        # node_configs, node_states, inputs ! prefix > to node_id
        f.construct()
        return graph

    @classmethod
    def from_config(
        cls,
        rule_id: str,
        action: RuleAction,
        rule_name: str,
        conditions: list[RuleCondition],
    ) -> "Rule":
        """Build rule from config"""
        rule_id = f"{rule_id}-{action.id}"
        configs = {}
        for node in action.graph_config.nodes:
            if node.name == "probe" or not node.config:
                continue
            # if node.name in {"alarm", "threshold"} and "vars" in node.config:
            #     node.config["vars"] = [VarItem(**v) for v in node.config["vars"]]
            configs[f"{rule_id}::{node.name}"] = node.config
        scopes, inputs = set(), set()
        for a in action.inputs:
            scopes.add(a.sender_id)
            inputs.add(a.probe_id)
        return Rule(
            id=rule_id,
            match_labels=frozenset(
                frozenset(sys.intern(label) for label in c.labels) for c in conditions
            ),
            exclude_labels=None,
            graph_config=action.graph_config,
            match_scopes=scopes,
            inputs=inputs,
            alarms=[],
            configs=configs,
        )
