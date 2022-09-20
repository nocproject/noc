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

    def set_and_get_activated_inputs(
        self, node, name: str, value: ValueType
    ) -> Optional[Dict[str, ValueType]]:
        """
        Set node's input to the value.
        Return the dict of collected input values
        if all required inputs are activated.

        :param node: BaseNode instance
        :param name: Input name
        :param value: Input value
        :returns: None if non-activated inputs
            still remain, dict of input values
            otherwise.
        """
        node_id = node.node_id
        inputs = self.get_inputs(node_id)
        if inputs.get(name) is None:
            return None  # Already activated
        # Activate value
        inputs[name] = value
        # Check if all required inputs is activated
        req_left = self.req_left.get(node_id)
        if req_left is None:
            raise RuntimeError("Required inputs count is not initialized")
        if node.is_required_input(name):
            req_left -= 1
            self.req_left[node_id] = req_left
            if req_left <= 0:
                return inputs  # All required inputs are activated
        return None

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
