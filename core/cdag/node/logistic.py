# ----------------------------------------------------------------------
# LogisticNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from math import exp

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class LogisticConfig(BaseModel):
    L: float = 1.0
    k: float = 1.0


class LogisticNode(BaseCDAGNode):
    """
    Get logistic activation function of 'x', lying in [0..L] with stepness of `k`
    """

    name = "logistic"
    config_cls = LogisticConfig
    categories = [Category.MATH, Category.ACTIVATION]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        if not self.config.k:
            return None
        return self.config.L / (1.0 + exp(-self.config.k * x))
