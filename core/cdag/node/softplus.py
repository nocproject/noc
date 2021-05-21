# ----------------------------------------------------------------------
# SoftPlusNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from math import log1p, exp

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class SoftPlusConfig(BaseModel):
    k: float = 1.0


class SoftPlusNode(BaseCDAGNode):
    """
    Get softplus activation function of 'x' with sharpness of `k`
    """

    name = "softplus"
    config_cls = SoftPlusConfig
    categories = [Category.MATH, Category.ACTIVATION]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        if not self.config.k:
            return None
        return log1p(exp(float(x) * self.config.k)) / self.config.k
