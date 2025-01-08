# ----------------------------------------------------------------------
# Transaction
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, Tuple

# NOC modules
from .typing import ValueType


class Transaction(object):
    def __init__(self, cdag):
        self.cdag = cdag
        # id(node) -> value
        self.inputs: Dict[str, Dict[str, ValueType]] = {}
        # id(node) -> int
        self.req_left: Dict[str, int] = {}
        self._states: Dict[Tuple[str, str], Any] = {}

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
        inputs = self.inputs.get(node)
        if inputs is None:
            # Initialize node inputs
            inputs = node.get_initial_inputs()
            self.inputs[node] = inputs
            # Initialize required count
            self.req_left[node] = node.req_inputs_count + node.req_config_inputs_count
            # Deduce amount of required initial inputs set
            if inputs:
                self.req_left[node] -= sum(1 for n in inputs if node.is_required_input(n))
        return inputs

    def is_ready(self, node) -> bool:
        """
        Decrement required node's inputs count and return
        true if all inputs are activated

        :param node: BaseNode instance
        :returns: True if all required nodes are activated, False otherwise
        """
        req_left = self.req_left[node]  # Can raise KeyError
        if req_left <= 1:
            return True
        self.req_left[node] -= 1
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
        d = state.dict()
        if d:
            self._states[node.node_id, node.name] = d

    def get_changed_state(self) -> Dict[Tuple[str, str], Any]:
        """
        Get side effect of transaction
        :return:
        """
        return self._states
