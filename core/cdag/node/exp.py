# ----------------------------------------------------------------------
# ExpNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from math import exp

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class ExpNode(BaseCDAGNode):
    """
    Get exponent of 'x'
    """

    name = "exp"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        return exp(x)
