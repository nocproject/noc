# ---------------------------------------------------------------------
# Topo types
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass


@dataclass
class ObjectSnapshot:
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
    links: list[int] | None = None
    uplinks: list[int] | None = None
