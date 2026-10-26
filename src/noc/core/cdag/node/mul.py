# ----------------------------------------------------------------------
# MulNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

from .base import BaseCDAGNode, Category, ValueType


class MulNode(BaseCDAGNode):
    """
    Multiply `x` by `y`
    """

    name = "mul"
    categories = [Category.OPERATION]

    def get_value(self, x: ValueType, y: ValueType) -> ValueType | None:
        return x * y
