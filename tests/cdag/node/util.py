# ----------------------------------------------------------------------
# Testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.typing import ValueType
from noc.core.cdag.tx import Transaction


class NodeCDAG(object):
    def __init__(self, node_type: str, config=None, state=None):
        self.cdag = CDAG("test", state or {})
        self.node = self.cdag.add_node("node", node_type, config=config)
        self.measure_node = self.cdag.add_node("measure", "none")
        self.node.subscribe(self.measure_node, "x")
        self.tx = self.cdag.begin()

    def get_node(self) -> BaseCDAGNode:
        return self.node

    def activate(self, name: str, value: ValueType):
        self.tx.activate("node", name, value)

    def get_value(self) -> Optional[ValueType]:
        """
        Get measured value, None if node is not activated
        :return:
        """
        i = self.tx.get_inputs(self.measure_node)
        return i["x"]  # None node has `x` input

    def is_activated(self):
        return not any(True for v in self.tx.get_inputs(self.node).values() if v is None)

    def begin(self) -> Transaction:
        self.tx = self.cdag.begin()
        return self.tx

    def get_changed_state(self) -> Dict[str, Any]:
        return self.tx.get_changed_state()
