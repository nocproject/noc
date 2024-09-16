# ---------------------------------------------------------------------
# Attach to module
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Iterable

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.inv.models.error import ConnectionError
from noc.core.resource import from_resource
from ..result import Result


@dataclass
class ModulePosition(object):
    obj: Object
    name: str

    def as_resource(self) -> str:
        """
        Convert position to resource.
        """
        return f"o:{self.obj.id}:{self.name}"

    @classmethod
    def from_resource(cls, res: str) -> "ModulePosition | None":
        """
        Get position from resource.
        """
        obj: Object
        obj, name = from_resource(res)
        if not obj or not name:
            return None
        return ModulePosition(obj=obj, name=name)


def attach(obj: Object, /, position: ModulePosition) -> Result:
    """
    Insert module into object.

    Args:
        obj: attached item.
        position: position to attach.

    Returns:
        Result item.
    """
    try:
        obj.attach(position.obj, position.name)
    except ConnectionError as e:
        return Result(status=False, message=str(e))
    return Result(status=True, message="Item attached")


def get_free(container: Object, obj: Object) -> Iterable[ModulePosition]:
    """
    Get free positions to which module can be attached.

    Args:
        container: Root module.
        obj: Attached objects.

    Returns:
        Yields ModulePosition for free slots.
    """

    def inner(m: Object) -> Iterable[ModulePosition]:
        # Get used slots
        used_slots = set(m.iter_used_connections())
        # Do not count currently occupied slot
        if obj.parent == m and obj.parent_connection and obj.parent_connection in used_slots:
            used_slots.remove(obj.parent_connection)
            # Oversized
            if size > 1:
                for cn in m.model.iter_next_connections(obj.parent_connection, size - 1):
                    if cn.name in used_slots:
                        used_slots.remove(cn.name)
        # Iterate through modules
        for cn in m.model.connections:
            # Leave only inner and unused connections
            if not cn.is_inner or cn.name in used_slots:
                continue
            # Check compatibility
            is_compatible, _ = ObjectModel.check_connection(cn, outer)
            if not is_compatible:
                continue
            # Process oversized modules
            if size > 1:
                next_conns = set(cn.name for cn in m.model.iter_next_connections(cn.name, size - 1))
                if len(next_conns) != size - 1 or next_conns.intersection(used_slots):
                    continue  # Cannot be placed here
            # Available
            yield ModulePosition(obj=m, name=cn.name)
        # Recursively process children
        for child in m.iter_children():
            if child == obj:
                continue  # Same object
            yield from inner(child)

    outer = obj.model.get_outer()
    if not outer:
        return
    # Oversized?
    size = obj.occupied_slots
    yield from inner(container)
