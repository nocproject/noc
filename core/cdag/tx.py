# ----------------------------------------------------------------------
# Transaction
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from .typing import ValueType


class Transaction(object):
    def __init__(self, cdag):
        self.cdag = cdag
        self.inputs: [Dict[str, Dict[str, ValueType]]] = {}
        self._states: Dict[str, Any] = {}

    def activate(self, node: str, name: str, value: ValueType) -> None:
        # Find node
        n = self.cdag.get_node(node)
        if not n:
            raise KeyError(f"Invalid node {node}")
        n.activate(self, name, value)

    def get_inputs(self, node) -> Dict[str, ValueType]:
        """
        Get node's actual inputs
        :param node:
        :return:
        """
        if node.node_id not in self.inputs:
            const_inputs = node.const_inputs
            self.inputs[node.node_id] = {n: const_inputs.get(n) for n in node.iter_inputs()}
        return self.inputs[node.node_id]

    def update_state(self, node) -> None:
        """
        Mark state as changed

        :param node:
        :return:
        """
        state = node.get_state()
        if state:
            self._states[node.node_id] = state.dict()

    def get_changed_state(self) -> Dict[str, Any]:
        """
        Get side effect of transaction
        :return:
        """
        return self._states
