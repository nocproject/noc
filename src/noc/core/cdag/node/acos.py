# ----------------------------------------------------------------------
# ACosNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import acos

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class ACosNode(BaseCDAGNode):
    """
    Get arccosinus of 'x'
    """

    name = "acos"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return acos(x)
