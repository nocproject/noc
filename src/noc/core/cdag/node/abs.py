# ----------------------------------------------------------------------
# AbsNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class AbsNode(BaseCDAGNode):
    """
    Get absolute value of 'x'
    """

    name = "abs"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return abs(x)
