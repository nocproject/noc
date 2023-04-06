# ---------------------------------------------------------------------
# Topo types
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ObjectSnapshot(object):
    """
    Managed object snapshot for topology service.

    Object snapshot is the current representation
    of object in the database.

    Attributes:
        id: Managed Object's id.
        level: Managed Object's level.
        links: Optional list of linked neighbors.
        uplinks: Optional list of uplink neighbors.
    """

    id: int
    level: int
    links: Optional[List[int]] = None
    uplinks: Optional[List[int]] = None
