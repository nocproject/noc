# ----------------------------------------------------------------------
# NegNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class NegNode(BaseCDAGNode):
    """
    Negate 'x'
    """

    name = "neg"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return -x
