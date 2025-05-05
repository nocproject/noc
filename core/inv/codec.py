# ---------------------------------------------------------------------
# Encode and decode Inventory Objects and Connections
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional, Union

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, Field

# NOC modules
from .result import Result
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection, ObjectConnectionItem


class ModelItem(BaseModel):
    uuid: str
    name: str


class ObjectConnectionItem_(BaseModel):
    name: str  # имя connection (из модели)
    object: str  # (ссылку надо на объект чтоли?) - структура Object (для connection типа o )
    # todo
    # по факту сейчас сюда пишутся поля из ObjectConnectionData
    # в name - name, в object - interface_name


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
    mode: Optional[str] = None
    connections: Optional[list[ObjectConnectionItem_]] = None
    additional_connections: Optional[list[str]] = None
    data: list[ObjectDataItem]
    cross: Optional[list[CrossItem]] = None


class PointItem(BaseModel):
    object: str
    name: str


class ConnectionItem(BaseModel):
    id: Optional[str] = None
    connection: list[PointItem]


class InvData(BaseModel):
    """Structure for encode/decode Inventory Objects"""

    type: str = Field(serialization_alias="$type")
    version: str = Field(serialization_alias="$version")
    objects: list[ObjectItem]
    connections: list[ConnectionItem]


def encode(iter: Iterable[Object]) -> InvData:
    """
    Encode several Inventory Objects with all it's descendants into pydatic-structure.
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

    def generate_object_item(object: Object) -> ObjectItem:
        """Generate ObjectItem structure for Object"""
        o_model: ModelItem = ModelItem(uuid=str(object.model.uuid), name=object.model.name)
        o_connections: list[ObjectConnectionItem_] = [
            ObjectConnectionItem_(
                name=c.name,
                object=c.interface_name,
            )
            for c in object.connections
        ]
        o_data: list[ObjectDataItem] = [
            ObjectDataItem(
                interface=d.interface,
                attr=d.attr,
                scope=d.scope,
                value=d.value,
            )
            for d in object.data
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
            "mode": getattr(object, "mode", None),
            "connections": o_connections,
            "additional_connections": object.additional_connections,
            "data": o_data,
            "cross": o_cross,
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
            # x = conn.connection[0].object
            # y = conn.connection[1].object
            # x_iw = conn.connection[0].object.is_wire
            # y_iw = conn.connection[1].object.is_wire
            # xxx = "+++++" if x_iw or y_iw else "-"
            # print(f"* {conn.id} {conn} {x_iw} {y_iw} {xxx} {x.id} {y.id}")

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
        print(f"Found direct connections: {len(direct_connections)}")
        print(f"Found cable connections {len(cable_connections)}")
        return direct_connections + cable_connections

    objects = []
    object_ids = []
    for parent_object in iter:
        for obj in iter_object_tree(parent_object, exclude_cables=True):
            objects.append(generate_object_item(obj))
            object_ids.append(obj.id)
    connections = []
    for conn in get_connections(object_ids):
        connections.append(conn)
    return InvData(
        type="inventory",
        version="1.0",
        objects=objects,
        connections=connections,
    )


def decode(root: Object, data: InvData) -> Result:
    return Result(status=True, message="Objects imported successfully")
