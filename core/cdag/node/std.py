# ----------------------------------------------------------------------
# StdNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import numpy as np

# NOC modules
from .mean import MeanNode


class StdNode(MeanNode):
    """
    Calculate standard deviation
    """

    name = "std"

    def get_stats(self, values: np.array) -> float:
        return np.std(values)
