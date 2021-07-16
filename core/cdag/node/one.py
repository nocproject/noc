# ----------------------------------------------------------------------
# OneNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseCDAGNode, Category, ValueType


class OneNode(BaseCDAGNode):
    """
    Replicates input to output
    """

    name = "one"
    categories = [Category.UTIL]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        return x
