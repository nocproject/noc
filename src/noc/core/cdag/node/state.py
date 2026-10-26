# ----------------------------------------------------------------------
# StateNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

from .base import BaseCDAGNode, Category, ValueType


class StateNodeState(BaseModel):
    value: ValueType | None = None


class StateNode(BaseCDAGNode):
    """
    Save input value to a state value 'value' and proxies input to output
    """

    name = "state"
    state_cls = StateNodeState
    dot_shape = "doubleoctagon"
    categories = [Category.DEBUG]

    def get_value(self, x: ValueType) -> ValueType | None:
        self.state.value = x
        return x
