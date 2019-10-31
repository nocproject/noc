# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectLevel goal
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
from typing import Optional

# NOC modules
from noc.sa.models.managedobject import ManagedObject

from .base import BaseGoal


class ManagedObjectLevelGoal(BaseGoal):
    """
    Matches when current level greater of equal to defined
    """

    TOWARDS_COST = 1
    SAME_LEVEL_COST = 10
    BACKWARDS_COST = 100

    def __init__(self, level):
        super(ManagedObjectLevelGoal, self).__init__()
        self.level = level

    def cost_estimate(self, neighbor, current=None):
        # type: (ManagedObject, Optional[ManagedObject]) -> int
        if current:
            current_level = current.object_profile.level
            neighbor_level = neighbor.object_profile.level
            if current_level == neighbor_level:
                return self.SAME_LEVEL_COST
            elif current_level > neighbor_level:
                return self.BACKWARDS_COST
            else:
                return self.TOWARDS_COST
        return self.DEFAULT_COST

    def is_goal(self, obj):
        # type: (ManagedObject) -> bool
        return obj.object_profile.level >= self.level
