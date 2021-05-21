# ----------------------------------------------------------------------
# SubNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class SubNode(BaseCDAGNode):
    """
    Subtract `y` from `y`
    """

    name = "sub"
    categories = [Category.OPERATION]

    def get_value(self, x: ValueType, y: ValueType) -> Optional[ValueType]:
        return x - y
