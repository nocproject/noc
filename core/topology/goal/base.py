# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseGoal class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Optional

# NOC modules
from noc.sa.models.managedobject import ManagedObject


class BaseGoal(object):
    DEFAULT_COST = 1
    DROP_COST = 0xFFFFFF

    def __init__(self) -> None:
        pass

    def cost_estimate(
        self, neighbor: ManagedObject, current: Optional[ManagedObject] = None
    ) -> int:
        """
        Heuristic cost estimate for A* algorithm.
        Cost of going to the goal across this path from `current` to `neighbor` node

        :param neighbor: Neighbor ManagedObject instance
        :param current: optional Current ManagedObject instance
        :return: Cost estimate
        """
        return self.DEFAULT_COST

    def is_goal(self, obj: ManagedObject) -> bool:
        """
        Check object is valid goal (end of path)

        :param obj: ManagedObject
        :return: True, if `obj` is the end of path
        """
        return False

    def __neg__(self: "BaseGoal") -> "BaseGoal":
        return NotGoal(self)

    def __and__(self, other: "BaseGoal") -> "BaseGoal":
        return AndGoal(self, other)

    def __or__(self, other: "BaseGoal") -> "BaseGoal":
        return OrGoal(self, other)


class AndGoal(BaseGoal):
    def __init__(self, left: BaseGoal, right: BaseGoal) -> None:
        super(BaseGoal, self).__init__()
        self.left = left
        self.right = right

    def cost_estimate(
        self, neighbor: ManagedObject, current: Optional[ManagedObject] = None
    ) -> int:
        return max(
            self.left.cost_estimate(neighbor, current), self.right.cost_estimate(neighbor, current)
        )

    def is_goal(self, obj: ManagedObject) -> bool:
        return self.left.is_goal(obj) and self.right.is_goal(obj)


class OrGoal(BaseGoal):
    def __init__(self, left: BaseGoal, right: BaseGoal) -> None:
        super(BaseGoal, self).__init__()
        self.left = left
        self.right = right

    def cost_estimate(
        self, neighbor: ManagedObject, current: Optional[ManagedObject] = None
    ) -> int:
        return max(
            self.left.cost_estimate(neighbor, current), self.right.cost_estimate(neighbor, current)
        )

    def is_goal(self, obj: ManagedObject) -> bool:
        return self.left.is_goal(obj) or self.right.is_goal(obj)


class NotGoal(BaseGoal):
    def __init__(self, goal: BaseGoal) -> None:
        super(BaseGoal, self).__init__()
        self.goal = goal

    def is_goal(self, obj: ManagedObject) -> bool:
        return not self.goal.is_goal(obj)
