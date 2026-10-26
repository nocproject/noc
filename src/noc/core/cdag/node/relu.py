# ----------------------------------------------------------------------
# ReLUNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

from .base import BaseCDAGNode, Category, ValueType


class ReLUNode(BaseCDAGNode):
    """
    Get ReLU activation function of 'x'
    """

    name = "relu"
    categories = [Category.MATH, Category.ACTIVATION]

    def get_value(self, x: ValueType) -> ValueType | None:
        return max(x, 0)
