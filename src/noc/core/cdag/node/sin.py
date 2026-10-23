# ----------------------------------------------------------------------
# SinNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import sin

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class SinNode(BaseCDAGNode):
    """
    Get sinus of 'x'
    """

    name = "sin"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return sin(x)
