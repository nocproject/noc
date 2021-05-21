# ----------------------------------------------------------------------
# Eq Node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# DivNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class CompConfig(BaseModel):
    true_level: ValueType = 1
    false_level: ValueType = 0
    epsilon: float = 1e-5


class EqNode(BaseCDAGNode):
    """
    Compare `x` and `y`. Activate with `true_level` if difference is lower than `epsilon`,
    activate with `false_level` otherwise
    """

    name = "eq"
    config_cls = CompConfig
    categories = [Category.COMPARE]

    def get_value(self, x: ValueType, y: ValueType) -> Optional[ValueType]:
        if abs(x - y) <= self.config.epsilon:
            return self.config.true_level
        return self.config.false_level
