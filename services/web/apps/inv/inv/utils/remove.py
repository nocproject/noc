# ---------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterable

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection


def remote_all(root: Object) -> int:
    """
    Remove all nested objects and connections.

    Args:
        root: Root object.

    Returns:
        Number of deleted objects.
    """
    objects = list(_iter_all(root))
    # Remove connections
    _drop_connections(objects)
    # Remove objects
    # Reversed order allows to delete connections safely
    for obj in reversed(objects):
        obj.delete()
    return len(objects)


def remove_root(root: Object, parent: Object, /, keep_connections: bool = False) -> int:
    """
    Remove root object and move children to parent.

    Args:
        root: Object to remove.
        parent: Parent to move children.
        keep_connections: Keep or drop children connections.

    Returns:
        Number of deleted objects.
    """
    # Drop necessary connections
    if keep_connections:
        _drop_connections([root])
    else:
        _drop_connections(_iter_all(root))
    # Reconnect children
    for child in root.iter_children():
        child.parent = parent
        child.parent_connection = None
        child.save()
    # Delete root
    root.delete()
    return 1


def _drop_connections(objects: Iterable[Object]) -> None:
    """
    Drop connections to objects.

    Args:
        objects: Iterable of objects
    """
    locals = {o.id for o in objects}
    wires: set[Object] = set()
    # Get all connections
    for conn in ObjectConnection.objects.filter(connection__object__in=list(locals)):
        if len(conn.connection) != 2:
            continue  # @todo: Process later
        x, y = conn.connection
        if x.object.id in locals and y.object.is_wire:
            wires.add(y.object)
        elif y.object.id in locals and x.object.is_wire:
            wires.add(x.object)
        # Drop connnection
        conn.delete()
    # Drop cables
    for obj in wires:
        obj.delete()


def _iter_all(root: Object) -> Iterable[Object]:
    """
    Iterate all objects behind root.

    Objects are ordered from up to down.

    Args:
        root: Root object

    Returns:
        Yields object items.
    """
    yield root
    for child in root.iter_children():
        yield from _iter_all(child)
