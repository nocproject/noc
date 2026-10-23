# ----------------------------------------------------------------------
# ATanNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import atan

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class ATanNode(BaseCDAGNode):
    """
    Get arctangens of 'x'
    """

    name = "atan"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return atan(x)
