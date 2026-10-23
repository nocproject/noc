# ----------------------------------------------------------------------
# DivNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class DivNode(BaseCDAGNode):
    """
    Divide `x` by `y`
    """

    name = "div"
    categories = [Category.OPERATION]

    def get_value(self, x: ValueType, y: ValueType) -> ValueType | None:
        if not y:
            return None
        return x / y
