# ----------------------------------------------------------------------
# TanNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import tan

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class TanNode(BaseCDAGNode):
    """
    Get tangens of 'x'
    """

    name = "tan"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return tan(x)
