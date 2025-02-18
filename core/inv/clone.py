# ---------------------------------------------------------------------
# Clone group
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object, ObjectAttr
from noc.inv.models.objectconnection import ObjectConnection, ObjectConnectionItem


# interface, attr to clean from clone
_SKIPPED_ATTRS = {
    ("stack", "member"),
    ("asset", "serial"),
    ("asset", "asset_no"),
    ("management", "managed_object"),
}

_ROOT_SKIPPED_ATTRS = {
    ("rackmount", "position"),
    ("rackmount", "side"),
    ("rackmount", "shift"),
}

# Fields to ignore during clone
_IGNORED_FIELDS = {"id", "bi_id", "remote_system", "remote_id"}


def clone(root: Object, /, clone_connections: bool = False) -> Object:
    """
    Clone object and all children.

    Cloned object will be placed to same parent.

    Args:
        root: Root object.
        clone_connection: Clone all internal connections as well.

    Returns:
        Cloned root object.
    """

    def to_skip(d: ObjectAttr) -> bool:
        k = (d.interface, d.attr)
        return k in _SKIPPED_ATTRS

    def to_skip_root(d: ObjectAttr) -> bool:
        k = (d.interface, d.attr)
        return k in _SKIPPED_ATTRS or k in _ROOT_SKIPPED_ATTRS

    def clone_object(obj: Object, /, name: str | None = None, is_root: bool = False) -> Object:
        cloned = Object(**{k: v for k, v in obj._data.items() if k not in _IGNORED_FIELDS})
        skipper = to_skip_root if is_root else to_skip
        cloned.data = [d for d in cloned.data if not skipper(d)]
        if name:
            cloned.name = name
        cloned.save()
        return cloned

    def inner_clone(obj: Object, /, name: str | None = None, is_root: bool = False) -> Object:
        # Clone
        cloned = clone_object(obj, name=name, is_root=is_root)
        c_map[obj] = cloned
        # Clone children
        for child in obj.iter_children():
            cloned_child = inner_clone(child)
            cloned_child.parent = cloned
            cloned_child.parent_connection = child.parent_connection
            cloned_child.save()
        return cloned

    def connect_cloned() -> None:
        # cable id -> [(cable item, object item)]
        cables: dict[ObjectId, list[tuple[ObjectConnectionItem, ObjectConnectionItem]]] = {}
        # Get cables
        for conn in ObjectConnection.objects.filter(connection__object__in=[o.id for o in c_map]):
            if len(conn.connection) != 2:
                continue  # @todo: Process later
            x, y = conn.connection
            cable = y.object if x.object in c_map else x.object
            if cable.is_wire:
                cables[cable.id] = []
        # Process cable connections
        for conn in ObjectConnection.objects.filter(connection__object__in=list(cables)):
            if len(conn.connection) != 2:
                continue  # @todo: Process later
            x, y = conn.connection
            if x.object.id in cables and y.object in c_map:
                cables[x.object.id].append((x, y))
            elif y.object.id in cables and x.object in c_map:
                cables[y.object.id].append((y, x))
        # Clone cables
        for items in cables.values():
            if len(items) != 2:
                continue
            (cable_x, obj_x), (cable_y, obj_y) = items
            new_cable = clone_object(cable_x.object)
            ObjectConnection(
                connection=[
                    ObjectConnectionItem(object=new_cable, name=cable_x.name),
                    ObjectConnectionItem(object=c_map[obj_x.object], name=obj_x.name),
                ]
            ).save()
            ObjectConnection(
                connection=[
                    ObjectConnectionItem(object=new_cable, name=cable_y.name),
                    ObjectConnectionItem(object=c_map[obj_y.object], name=obj_y.name),
                ]
            ).save()

    # old -> new object map
    c_map: dict[Object, Object] = {}
    cloned_root = inner_clone(root, name=f"{root.name} (Clone)", is_root=True)
    if root.parent_connection:
        # Attach to nearest container
        cloned_root.parent = root.get_container()
        cloned_root.parent_connection = None
        cloned_root.save()
    if clone_connections:
        connect_cloned()
    return cloned_root
