# ----------------------------------------------------------------------
# CosNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import cos

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class CosNode(BaseCDAGNode):
    """
    Get cosinus of 'x'
    """

    name = "cos"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return cos(x)
