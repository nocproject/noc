# ----------------------------------------------------------------------
# NoneNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseCDAGNode, Category, ValueType


class NoneNode(BaseCDAGNode):
    """
    Suppress any output
    """

    name = "none"
    categories = [Category.UTIL]

    def get_value(self, x: ValueType) -> ValueType | None:
        return None
