# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# UpwardsConstraint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from .base import BaseConstraint


class UpwardsConstraint(BaseConstraint):
    """
    Deny decreasing managed object levels when passing through the path
    """

    def is_valid_neighbor(self, current: ManagedObject, neighbor: ManagedObject) -> bool:
        return current.object_profile.level <= neighbor.object_profile.level
