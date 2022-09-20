# ----------------------------------------------------------------------
# Transaction
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, Optional

# NOC modules
from .typing import ValueType


class Transaction(object):
    def __init__(self, cdag):
        self.cdag = cdag
        self.inputs: Dict[str, Dict[str, ValueType]] = {}
        self.req_left: Dict[str, int] = {}
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
        node_id = node.node_id
        inputs = self.inputs.get(node_id)
        if not inputs:
            # Initialize node inputs
            inputs = node.get_initial_inputs()
            self.inputs[node_id] = inputs
            # Initialize required count
            self.req_left[node_id] = node.get_required_inputs_count()
        return inputs

    def is_ready(self, node) -> bool:
        """
        Decrement required node's inputs count and return
        true if all inputs are activated

        :param node: BaseNode instance
        :returns: True if all required nodes are activated, False otherwise
        """
        node_id = node.node_id
        req_left = self.req_left[node_id]  # Can raise KeyError
        if req_left <= 1:
            return True
        self.req_left[node_id] -= 1
        return False

    def update_state(self, node) -> None:
        """
        Mark state as changed

        :param node:
        :return:
        """
        state = node.get_state()
        if not state:
            return
        d = state.dict(exclude_none=True)
        if d:
            self._states[node.node_id] = d

    def get_changed_state(self) -> Dict[str, Any]:
        """
        Get side effect of transaction
        :return:
        """
        return self._states
