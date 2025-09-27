# ----------------------------------------------------------------------
# NthNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class NthNodeState(BaseModel):
    values: List[ValueType] = []


class NthNodeConfig(BaseModel):
    n: int = 1


class NthNode(BaseCDAGNode):
    """
    Return N-th previous measure (Induce n-step delay).
    `n` == 1 - last measure
    """

    name = "nth"
    config_cls = NthNodeConfig
    state_cls = NthNodeState
    categories = [Category.WINDOW]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        if self.config.n <= 0:
            return x
        # Fill window
        self.state.values.insert(0, x)
        lv = len(self.state.values)
        if lv <= self.config.n:
            return None  # Window is not filled
        if lv > self.config.n:
            # Trim
            self.state.values = self.state.values[: self.config.n + 1]
        return self.state.values[self.config.n]
