# ----------------------------------------------------------------------
# SqrtNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import sqrt

from .base import BaseCDAGNode, Category, ValueType


class SqrtNode(BaseCDAGNode):
    """
    Get square root of 'x'
    """

    name = "sqrt"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        if x < 0:
            return None
        return sqrt(x)
