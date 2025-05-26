# ---------------------------------------------------------------------
# Encode and decode Inventory Objects and Connections
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Iterable, Optional, Union

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, Field

# NOC modules
from .result import Result
from noc.inv.models.object import Object, ObjectAttr, ObjectConnectionData
from noc.inv.models.objectconnection import ObjectConnection, ObjectConnectionItem
from noc.inv.models.objectmodel import Crossing, ObjectModel
from noc.inv.models.vendor import Vendor


@dataclass
class EncodeResultInfo:
    found_objects: Optional[int] = None
    found_connections_direct: Optional[int] = None
    found_connections_cable: Optional[int] = None


@dataclass
class DecodeResultInfo:
    found_objects: Optional[int] = None
    found_connections_direct: Optional[int] = None
    found_connections_cable: Optional[int] = None
    created_objects: Optional[int] = None
    created_connections_direct: Optional[int] = None
    created_cable_model: Optional[int] = None
    created_cable: Optional[int] = None
    created_connections_cable: Optional[int] = None


class ModelItem(BaseModel):
    uuid: str
    name: str


class ObjectConnectionItem_(BaseModel):
    name: str
    interface_name: str


class ObjectDataItem(BaseModel):
    interface: str
    attr: str
    scope: Optional[str] = None
    value: Union[int, float, str, list]


class CrossItem(BaseModel):
    input: str
    input_discriminator: Optional[str] = None
    output: str
    output_discriminator: Optional[str] = None
    gain_db: Optional[float] = None


class ObjectItem(BaseModel):
    id: str
    name: Optional[str] = None
    model: ModelItem
    parent: Optional[str] = None
    parent_connection: Optional[str] = None
    mode: Optional[str] = None
    data: list[ObjectDataItem]
    connections: Optional[list[ObjectConnectionItem_]] = None
    additional_connections: Optional[list[str]] = None
    cross: Optional[list[CrossItem]] = None


class PointItem(BaseModel):
    object: str
    name: str


class ConnectionItem(BaseModel):
    id: Optional[str] = None
    connection: list[PointItem]


class InvData(BaseModel):
    """Structure for encode/decode Inventory Objects"""

    type: str = Field("inventory", alias="$type")
    version: str = Field("1.0", alias="$version")
    objects: list[ObjectItem]
    connections: list[ConnectionItem]


def encode(iter: Iterable[Object]) -> (InvData, EncodeResultInfo):
    """
    Encode several Inventory Objects with all it's descendants into pydatic-structure.
    Uses in export Inventory Objects to file.
    Structure contains:
    - objects (all descendants of given in `iter` argument objects
    - connections between all found objects
    """

    def iter_object_tree(object: Object, exclude_cables: bool) -> Iterable["Object"]:
        """Get full tree with all descendants for object"""
        if exclude_cables and object.is_wire:
            return
        yield object
        for child in object.iter_children():
            if exclude_cables and child.is_wire:
                continue
            yield from iter_object_tree(child, exclude_cables)

    def generate_object_item(object: Object, is_root: bool) -> ObjectItem:
        """Generate ObjectItem structure for Object"""
        o_model: ModelItem = ModelItem(uuid=str(object.model.uuid), name=object.model.name)
        o_data: list[ObjectDataItem] = [
            ObjectDataItem(
                interface=d.interface,
                attr=d.attr,
                scope=d.scope,
                value=d.value,
            )
            for d in object.data
        ]
        o_connections: list[ObjectConnectionItem_] = [
            ObjectConnectionItem_(
                name=c.name,
                interface_name=c.interface_name,
            )
            for c in object.connections
        ]
        o_cross: list[CrossItem] = [
            CrossItem(
                input=c.input,
                input_discriminator=c.input_discriminator,
                output=c.output,
                output_discriminator=c.output_discriminator,
                gain_db=c.gain_db,
            )
            for c in object.cross
        ]
        oi_d = {
            "id": str(object.id),
            "name": object.name,
            "model": o_model,
            "parent": None if is_root else str(object.parent.id),
            "parent_connection": object.parent_connection,
            "mode": getattr(object, "mode", None),
            "data": o_data,
            "connections": o_connections or None,
            "additional_connections": object.additional_connections or None,
            "cross": o_cross or None,
        }
        return ObjectItem(**oi_d)

    def get_connections(object_ids: list[ObjectId]) -> list[ConnectionItem]:
        """Found all Connections for Objects in list"""

        def point_item(oci: ObjectConnectionItem) -> PointItem:
            return PointItem(object=str(oci.object.id), name=oci.name)

        def conn_item(oc: ObjectConnection) -> ConnectionItem:
            x, y = oc.connection
            return ConnectionItem(id=str(oc.id), connection=[point_item(x), point_item(y)])

        direct_connections: list[ConnectionItem] = []
        cables: dict[ObjectId, list[tuple[ObjectConnectionItem, ObjectConnectionItem]]] = {}
        # get all connections for Objects group
        for conn in ObjectConnection.objects.filter(connection__object__in=object_ids):
            if len(conn.connection) != 2:
                continue  # @todo: Process later
            x, y = conn.connection
            if x.object.is_wire or y.object.is_wire:
                # add cable
                # first connection is cable, second is object
                x, y = (x, y) if x.object.is_wire else (y, x)
                cable = x.object
                if cable.id not in cables:
                    cables[cable.id] = []
                cables[cable.id].append((x, y))
            else:
                # add direct connection
                if x.object.id in object_ids and y.object.id in object_ids:
                    direct_connections.append(conn_item(conn))
        # exclude cables having less than 2 connections
        cables = {k: v for k, v in cables.items() if len(v) == 2}
        cable_connections: list[ConnectionItem] = []
        # get cable connections only with both objects in Objects group
        for cable_id, cable_conns in cables.items():
            obj1_oci: ObjectConnectionItem = cable_conns[0][1]
            obj2_oci: ObjectConnectionItem = cable_conns[1][1]
            if obj1_oci.object.id in object_ids and obj2_oci.object.id in object_ids:
                cable_connections.append(
                    ConnectionItem(
                        connection=[
                            point_item(obj1_oci),
                            point_item(obj2_oci),
                        ],
                    )
                )
        info.found_connections_direct = len(direct_connections)
        info.found_connections_cable = len(cable_connections)
        return direct_connections + cable_connections

    info = EncodeResultInfo()
    objects = []
    object_ids = []
    for root_object in iter:
        for obj in iter_object_tree(root_object, exclude_cables=True):
            objects.append(generate_object_item(obj, obj is root_object))
            object_ids.append(obj.id)
    info.found_objects = len(objects)
    connections = []
    for conn in get_connections(object_ids):
        connections.append(conn)
    return (
        InvData(
            objects=objects,
            connections=connections,
        ),
        info,
    )


def decode(container: Object, data: InvData) -> (Result, DecodeResultInfo):
    """
    Decode Inventory Objects from pydatic-structure InvData and write it to database.
    Uses in import Inventory Objects from file.
    Following information is written:
    - all objects from structure
    - all connections from structure
    - also creates cable model and cable objects for cable connections.
    Cable connections defined as connections with null id in source file
    """
    info = DecodeResultInfo()
    info.found_objects = len(data.objects)
    info.found_connections_direct = sum(int(c.id is not None) for c in data.connections)
    info.found_connections_cable = len(data.connections) - info.found_connections_direct

    # Mapping between IDs of objects in source JSON and IDs of created in database objects
    # ID of object in JSON-file -> ID of created object
    o_map: dict[str, ObjectId] = {}

    # Create objects
    o_counter = 0
    for o in data.objects:
        parent = o_map[o.parent] if o.parent else container
        o_connections = (
            [ObjectConnectionData(**oci.dict()) for oci in o.connections] if o.connections else None
        )
        o_cross = [Crossing(**ci.dict()) for ci in o.cross] if o.cross else None
        obj = Object(
            name=o.name,
            model=ObjectModel.get_by_name(o.model.name),
            parent=parent,
            parent_connection=o.parent_connection,
            mode=o.mode,
            data=[ObjectAttr(**odi.dict()) for odi in o.data],
            connections=o_connections,
            additional_connections=o.additional_connections,
            cross=o_cross,
        ).save()
        o_map[o.id] = obj.id
        o_counter += 1
    info.created_objects = o_counter

    # Create cable model if needed
    CABLE_NAME = "optical cable sm"
    cable_model = ObjectModel.get_by_name(CABLE_NAME)
    if not cable_model:
        vendor = Vendor.get_by_code("NOC")
        cable_model = ObjectModel(
            name=CABLE_NAME,
            description=CABLE_NAME,
            data=[
                {
                    "interface": "length",
                    "attr": "length",
                    "value": 5,
                }
            ],
            vendor=vendor,
        ).save()
        info.created_cable_model = 1
    else:
        info.created_cable_model = 0

    def create_connection(c1: PointItem, c2: PointItem):
        c1 = c1.dict()
        c1["object"] = o_map[c1["object"]]
        c2 = c2.dict()
        c2["object"] = o_map[c2["object"]]
        ObjectConnection(
            connection=[
                ObjectConnectionItem(**c1),
                ObjectConnectionItem(**c2),
            ],
            type="testing",  # todo: delete this flag
        ).save()

    # Create connections
    c_counter_dir, c_counter_cab = 0, 0
    for c in data.connections:
        if c.id:
            # direct connections
            create_connection(c.connection[0], c.connection[1])
            c_counter_dir += 1
        else:
            # cable connections
            cable = Object(
                name="xcable",
                model=cable_model,
                # "parent", "parent_connection", "mode", "data", "connections",
                # "additional_connections", "cross" fields are empty for cables
            ).save()
            cable_virtual_id = f"c_{cable.id}"
            # use o_map for cable objects
            o_map[cable_virtual_id] = cable.id
            create_connection(c.connection[0], PointItem(object=cable_virtual_id, name="1"))
            create_connection(c.connection[1], PointItem(object=cable_virtual_id, name="2"))
            c_counter_cab += 1
    info.created_connections_direct = c_counter_dir
    info.created_connections_cable = c_counter_cab
    info.created_cable = c_counter_cab
    return Result(status=True, message="Objects decoded and wrote successfully"), info
