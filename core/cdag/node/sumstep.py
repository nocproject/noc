# ----------------------------------------------------------------------
# SumStepNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from enum import Enum

# NOC modules
from .base import ValueType, Category
from .window import WindowNode, WindowConfig
import itertools


class StepDirection(str, Enum):
    INC = "inc"
    DEC = "dec"
    ABS = "abs"


class SumStepNodeConfig(WindowConfig):
    direction: StepDirection = StepDirection.ABS


class SumStepNode(WindowNode):
    """
    Calculate sum of increments in the window.
    """

    name = "sumstep"
    config_cls = SumStepNodeConfig
    categories = [Category.WINDOW]

    def get_window_value(
        self, values: List[ValueType], timestamps: List[int]
    ) -> Optional[ValueType]:
        if self.config.direction == StepDirection.INC:
            return sum(x1 - x0 for x0, x1 in itertools.pairwise(values) if x1 > x0)
        if self.config.direction == StepDirection.DEC:
            return sum(x0 - x1 for x0, x1 in itertools.pairwise(values) if x1 < x0)
        return sum(abs(x1 - x0) for x0, x1 in itertools.pairwise(values))
