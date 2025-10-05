# ----------------------------------------------------------------------
# ObjectGoal
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Optional, List, Set, Dict

# NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject
from .base import BaseGoal


class ManagedObjectGoal(BaseGoal):
    SEGMENT_COST_MULTIPLIER = 100
    HORIZONTAL_COST = 10

    def __init__(self, obj: ManagedObject) -> None:
        super().__init__()
        self.object = obj
        # Use A* acceleration
        self.use_segment_path = True
        # Heuristic weight is the number of segments to be passed to goal
        self.hw: Dict[NetworkSegment, int] = {}

    def segment_cost_estimate(self, neighbor, current=None):
        if not self.hw:
            # Not initialized still
            self._init_weights(neighbor)
            if not self.use_segment_path:
                # No segment paths, disabled during weight calculation
                return 0
        cost = self.hw.get(neighbor.segment)
        if cost is not None:
            return cost
        if current and neighbor.segment.enable_horizontal_transit:
            # Horizontal transit modifier
            # Add horizontal transit segment
            cost = self.hw[current.segment] + self.HORIZONTAL_COST
            self.hw[neighbor.segment] = cost
            return cost
        return self.DROP_COST

    def cost_estimate(
        self, neighbor: ManagedObject, current: Optional[ManagedObject] = None
    ) -> int:
        cost = self.DEFAULT_COST
        # Apply segment penalty
        if self.use_segment_path:
            cost += self.segment_cost_estimate(neighbor, current)
        return cost

    def is_goal(self, obj: ManagedObject) -> bool:
        return self.object.id == obj.id

    def _init_weights(self, start: ManagedObject) -> None:
        """
        Initialize segment path from starting node

        :param start: Starting node Managed Object
        :return:
        """
        # We will restrict search only to segments along the path
        seg_path = self.get_segment_path(start, self.object)
        # Heuristic weight is the number of segments to be passed to goal
        pl = len(seg_path)
        self.hw = {}
        for i, s in enumerate(seg_path):
            self.hw[s] = (pl - i) * self.SEGMENT_COST_MULTIPLIER
        # Allow path via parent segment
        # if searching within one segment
        if len(seg_path) == 1 and seg_path[0].parent:
            self.hw[seg_path[0].parent] = 2 * self.SEGMENT_COST_MULTIPLIER
        self.use_segment_path = bool(self.hw)

    @staticmethod
    def get_segment_path(start: ManagedObject, goal: ManagedObject) -> List[NetworkSegment]:
        """
        Returns a list of segments laying between two management objects
        :param start: Managed Object instance
        :param goal: Managed Object instance
        :return: List of NetworkSegments
        """

        def merge_path(
            l1: List[NetworkSegment], l2: List[NetworkSegment], cross: Set[NetworkSegment]
        ) -> List[NetworkSegment]:
            ci = next(iter(cross))
            i1 = l1.index(ci)
            ri1 = l1[:i1]
            i2 = l2.index(ci)
            ri2 = list(reversed(l2[:i2]))
            return [*ri1, ci, *ri2]

        p1: List[NetworkSegment] = [start.segment]
        p2: List[NetworkSegment] = [goal.segment]
        while True:
            can_up1: bool = bool(p1[-1].parent)
            can_up2: bool = bool(p2[-1].parent)
            c = set(p1) & set(p2)
            if c:
                return merge_path(p1, p2, c)
            # Up mo1 path
            if can_up1:
                p1 += [p1[-1].parent]
                c = set(p1) & set(p2)
                if c:
                    return merge_path(p1, p2, c)
            # Up mo2 path
            if can_up2:
                p2 += [p2[-1].parent]
            elif not can_up2:
                raise ValueError("Cannot find path")
