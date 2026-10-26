# ----------------------------------------------------------------------
# ASinNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import asin

from .base import BaseCDAGNode, Category, ValueType


class ASinNode(BaseCDAGNode):
    """
    Get arcsinus of 'x'
    """

    name = "asin"
    categories = [Category.MATH]

    def get_value(self, x: ValueType) -> ValueType | None:
        return asin(x)
