# ---------------------------------------------------------------------
# ObjectModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
import re
from typing import Any, Optional, List, Tuple, Union, Iterable

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    UUIDField,
    ListField,
    DynamicField,
    EmbeddedDocumentListField,
    ObjectIdField,
    FloatField,
    BooleanField,
)
from mongoengine.errors import ValidationError
from pymongo import InsertOne, DeleteOne
import cachetools

# NOC modules
from noc.main.models.doccategory import category
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.change.decorator import change
from noc.pm.models.measurementunits import MeasurementUnits
from noc.core.discriminator import discriminator
from noc.main.models.glyph import Glyph
from .objectconfigurationrule import ObjectConfigurationRule
from .connectiontype import ConnectionType
from .connectionrule import ConnectionRule
from .unknownmodel import UnknownModel
from .vendor import Vendor
from .protocol import Protocol
from .facade import Facade

id_lock = Lock()

rx_composite_pins_validate = re.compile(r"\d+\-\d+")


class ModelAttr(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    interface = StringField()
    attr = StringField()
    value = DynamicField()

    def __str__(self) -> str:
        return "%s.%s = %s" % (self.interface, self.attr, self.value)

    @property
    def json_data(self) -> dict[str, Any]:
        return {
            "interface": self.interface,
            "attr": self.attr,
            "value": self.value,
        }


class ModeItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    description = StringField(required=False)
    is_default = BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    @property
    def json_data(self) -> dict[str, Any]:
        r = {"name": self.name}
        if self.description:
            r["description"] = self.description
        if self.is_default:
            r["is_default"] = self.is_default
        return r


class ProtocolVariantItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    protocol: "Protocol" = PlainReferenceField(Protocol, required=True)
    discriminator = StringField(required=False)
    direction = StringField(choices=[">", "<", "*"], default="*")
    data: list["ModelAttr"] = EmbeddedDocumentListField(ModelAttr)

    def __str__(self):
        return self.code

    def __hash__(self):
        return hash(self.code)

    @property
    def code(self) -> str:
        if not self.discriminator and self.direction == "*":
            return self.protocol.code
        elif not self.discriminator:
            return f"{self.direction}::{self.protocol.code}"
        return f"{self.direction}::{self.protocol.code}::{self.discriminator}"

    @property
    def json_data(self) -> dict[str, Any]:
        r = {
            "protocol__code": self.protocol.code,
            "direction": self.direction,
        }
        if self.discriminator:
            r["discriminator"] = self.discriminator
        return r

    def __eq__(self, other):
        r = self.protocol.id == other.protocol.id and self.direction == other.direction
        if not self.discriminator:
            return r
        return r and self.discriminator == other.discriminator

    def __contains__(self, item) -> bool:
        r = self.protocol.id == item.protocol.id and self.direction != item.direction
        if not self.discriminator:
            return r
        return r and self.discriminator == item.discriminator


class Crossing(EmbeddedDocument):
    """
    Dynamic/Static crossing.

    Attributes:
        input: Input slot name.
        input_discriminator: Input filter.
        output: Output slot name.
        output_discriminator: When not-empty, input to output mapping.
        gain_db: When non-empty, signal gain in dB.
        modes: List of modes for which crossing is applicable.
    """

    _meta = {"strict": False, "auto_create_index": False}
    input = StringField(required=True)
    input_discriminator = StringField(required=False)
    output = StringField(required=True)
    output_discriminator = StringField(required=False)
    gain_db = FloatField(required=False)
    modes = ListField(StringField(), required=False)

    def __str__(self) -> str:
        r = [self.input]
        if self.input_discriminator:
            r += [f": {self.input_discriminator}"]
        r += [" -> ", self.output]
        if self.output_discriminator:
            r += [f": {self.output_discriminator}"]
        if self.modes:
            r += f" ({', '.join(m for m in self.modes)})"
        return "".join(r)

    def update_params(self, input_discriminator: str, output_discriminator: str, gain_db):
        if self.input_discriminator != input_discriminator:
            self.input_discriminator == input_discriminator
        if self.output_discriminator != output_discriminator:
            self.output_discriminator = input_discriminator
        if self.gain_db != gain_db:
            self.gain_db = gain_db
        self.clean()

    def clean(self) -> None:
        if self.input_discriminator:
            try:
                discriminator(self.input_discriminator)
            except ValueError as e:
                msg = f"Invalid input_discriminator: {e}"
                raise ValidationError(msg) from e
        if self.output_discriminator:
            try:
                discriminator(self.output_discriminator)
            except ValueError as e:
                msg = f"Invalid output_discriminator: {e}"
                raise ValidationError(msg) from e
        super().clean()

    @property
    def json_data(self) -> dict[str, Any]:
        r: dict[str, Any] = {
            "input": self.input,
            "output": self.output,
        }
        if self.input_discriminator:
            r["input_discriminator"] = self.input_discriminator
        if self.output_discriminator:
            r["output_discriminator"] = self.output_discriminator
        if self.gain_db:
            r["gain_db"] = self.gain_db
        if self.modes:
            r["modes"] = self.modes
        return r


class ObjectModelConnection(EmbeddedDocument):
    _meta = {"strict": False, "auto_create_index": False}

    name = StringField()
    description = StringField()
    type = PlainReferenceField(ConnectionType)
    direction = StringField(choices=["i", "o", "s"])  # Inner slot  # Outer slot  # Connection
    gender = StringField(choices=["s", "m", "f"])
    combo = StringField(required=False)
    group = StringField(required=False)
    cross_direction: Optional[str] = StringField(
        choices=["i", "o", "s"], required=False
    )  # Inner  # Outer  # Any
    protocols: list["ProtocolVariantItem"] = EmbeddedDocumentListField(ProtocolVariantItem)
    cfg_context: str = StringField()
    internal_name = StringField(required=False)
    composite = StringField(required=False)
    composite_pins = StringField(required=False)
    data: list["ModelAttr"] = EmbeddedDocumentListField(ModelAttr)

    def __str__(self):
        return self.name

    def __eq__(self, other: "ObjectModelConnection"):
        return (
            self.name == other.name
            and self.description == other.description
            and self.type.id == other.type.id
            and self.direction == other.direction
            and self.gender == other.gender
            and self.combo == other.combo
            and self.cfg_context == other.cfg_context
            and self.group == other.group
            and self.cross_direction == other.cross_direction
            and self.protocols == other.protocols
            and self.internal_name == other.internal_name
            and self.composite == other.composite
            and self.composite_pins == other.composite_pins
            and self.data != other.data
        )

    @property
    def json_data(self) -> dict[str, Any]:
        r = {
            "name": self.name,
            "description": self.description,
            "type__name": self.type.name,
            "direction": self.direction,
            "gender": self.gender,
        }
        if self.combo:
            r["combo"] = self.combo
        if self.protocols:
            r["protocols"] = [pv.json_data for pv in self.protocols]
        if self.internal_name:
            r["internal_name"] = self.internal_name
        if self.composite:
            r["composite"] = self.composite
        if self.composite_pins:
            r["composite_pins"] = self.composite_pins
        if self.cross_direction:
            r["cross_direction"] = self.cross_direction
        if self.group:
            r["group"] = self.group
        if self.data:
            r["data"] = [d.json_data for d in self.data]
        return r

    def clean(self):
        if self.type.name in {"Composed", "Combined"} and (
            self.direction != "s" or self.gender != "s"
        ):
            raise ValidationError(
                'Direction and gender fields on Composed or Combined connection type must be "s"'
            )
        if self.composite_pins and not rx_composite_pins_validate.match(self.composite_pins):
            raise ValidationError("Composite pins not match format: N-N")
        super().clean()

    def get_protocols(self, context: str) -> list["ProtocolVariantItem"]:
        r = []
        for p in self.protocols:
            if context and p.cfg_context != context:
                continue
            r.append(p)
        return r

    @property
    def is_inner(self) -> bool:
        """
        Check if connection is inner.
        """
        return self.direction == "i"

    @property
    def is_outer(self) -> bool:
        """
        Check if connection is outer.
        """
        return self.direction == "o"

    @property
    def is_same_level(self) -> bool:
        """
        Check if connection is on same level.
        """
        return self.direction == "s"


class ObjectModelSensor(EmbeddedDocument):
    # Sensor name, may be duplicated for various collection methods
    name = StringField()
    description = StringField()
    units = PlainReferenceField(MeasurementUnits)
    # Register address for modbus access
    modbus_register = IntField()
    # Register address for modbus access
    modbus_format = StringField()
    # OID for SNMP access
    snmp_oid = StringField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> dict[str, Any]:
        r = {"name": self.name}
        if self.description:
            r["description"] = self.description
        r["units__code"] = self.units.code
        if self.modbus_register:
            r["modbus_register"] = self.modbus_register
            r["modbus_format"] = self.modbus_format
        if self.snmp_oid:
            r["snmp_oid"] = self.snmp_oid
        return r


@category
@change
@on_delete_check(check=[("inv.ModelMapping", "model"), ("inv.Object", "model")])
@on_save
class ObjectModel(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.objectmodels",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("vendor", "data.interface", "data.attr", "data.value"),
            ("data.interface", "data.attr", "data.value"),
            "labels",
        ],
        "json_collection": "inv.objectmodels",
        "json_unique_fields": ["name", "uuid"],
        "json_depends_on": ["inv.vendors", "inv.connectionrules", "pm.measurementunits"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    short_label = StringField(required=False)
    vendor: "Vendor" = PlainReferenceField(Vendor)
    connection_rule: "ConnectionRule" = PlainReferenceField(ConnectionRule, required=False)
    configuration_rule: "ObjectConfigurationRule" = PlainReferenceField(
        ObjectConfigurationRule, required=False
    )
    # Connection rule context
    cr_context = StringField(required=False)
    # Modes
    modes = EmbeddedDocumentListField(ModeItem, required=False)
    # Configuration Context Param
    # cfg_context_param = PlainReferenceField(ConfigurationParam, required=False)
    data: list["ModelAttr"] = EmbeddedDocumentListField(ModelAttr)
    connections: list["ObjectModelConnection"] = EmbeddedDocumentListField(ObjectModelConnection)
    # Static crossings
    cross: list[Crossing] = EmbeddedDocumentListField(Crossing)
    sensors: list["ObjectModelSensor"] = EmbeddedDocumentListField(ObjectModelSensor)
    plugins = ListField(StringField(), required=False)
    # Facades
    front_facade = PlainReferenceField(Facade, required=False)
    rear_facade = PlainReferenceField(Facade, required=False)
    # Glyph for navigation tree
    glyph = PlainReferenceField(Glyph, required=False)
    # Labels
    labels = ListField(StringField())
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _model_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ObjectModel"]:
        return ObjectModel.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["ObjectModel"]:
        return ObjectModel.objects.filter(name=name).first()

    def get_short_label(self) -> str:
        """
        Get label for schemes.

        Use short_label, if defined.
        Compose label otherwise.

        Returns:
            Short label for schemes.
        """
        if self.short_label:
            return self.short_label
        parts = []
        if self.vendor.code:
            parts.append(self.vendor.code[0])
        else:
            parts.append(self.vendor.full_name)
        parts.append(self.name.split("|")[-1].strip())
        return " ".join(parts)

    def get_data(
        self,
        interface: str,
        key: str,
        connection: Optional[str] = None,
        **params,
    ) -> Any:
        """
        Context ?
        :param interface: Model Interface name for data
        :param key: Data key on Model Interface
        :param connection: Data For connection
        :param context: Data Configuration Context
        :param params:
        :return:
        """
        # Getting default context from ObjectConfigurationRule
        if connection:
            c = self.get_model_connection(connection)
            if not c:
                raise ValueError("Unknown connection: %s" % c)
            data = c.data
        else:
            data = self.data
        for item in data:
            if item.interface == interface and item.attr == key:
                return item.value
        return None

    def on_save(self):
        # Fix connections
        if hasattr(self, "_changed_fields") and "connections" in self._changed_fields:
            self._ensure_connection_names()
        # Update connection cache
        ModelConnectionsCache.update_for_model(self)
        # Exclude all part numbers from unknown models
        self.clear_unknown_models()

    def has_connection(self, name: str) -> bool:
        if self.get_model_connection(name) is None:
            # Check twinax virtual connection
            return self.get_data("twinax", "twinax") and self.get_data("twinax", "alias") == name
        else:
            return True

    def has_connection_cross(self, name: str) -> bool:
        if self.get_model_connection(name).cross_direction:
            return True
        for c in self.cross:
            if name == c.input or name == c.output:
                return True
        return False

    def iter_connection_proposals(self, name: str) -> Iterable[Tuple["ObjectId", str]]:
        """
        Iterate possible connections from given one.

        Args:
            name: Connection name

        Returns:
            Yield tuples of (model id, connection names)
        """
        cn = self.get_model_connection(name)
        if not cn:
            return  # Connection not found
        c_types = cn.type.get_compatible_types(cn.gender)
        og = ConnectionType.OPPOSITE_GENDER[cn.gender]
        for cc in ModelConnectionsCache.objects.filter(type__in=c_types, gender=og):
            yield cc.model, cc.name

    def get_model_connection(self, name: str) -> Optional["ObjectModelConnection"]:
        for c in self.connections:
            if c.name == name or (c.internal_name and c.internal_name == name):
                return c
        return None

    @classmethod
    def check_connection(
        cls, lc: "ObjectModelConnection", rc: "ObjectModelConnection"
    ) -> Tuple[bool, str]:
        """

        :param lc:
        :param rc:
        :return:
        """
        # Check genders are compatible
        r_gender = ConnectionType.OPPOSITE_GENDER[rc.gender]
        if lc.gender != r_gender:
            return False, "Incompatible genders: %s - %s" % (lc.gender, rc.gender)
        # Check directions are compatible
        if (
            (lc.direction == "i" and rc.direction != "o")
            or (lc.direction == "o" and rc.direction != "i")
            or (lc.direction == "s" and rc.direction != "s")
        ):
            return False, "Incompatible directions: %s - %s" % (lc.direction, rc.direction)
        # Check types are compatible
        c_types = lc.type.get_compatible_types(lc.gender)
        if rc.type.id not in c_types:
            return False, "Incompatible connection types: %s - %s" % (lc.type.name, rc.type.name)
        return True, ""

    @classmethod
    def get_model(cls, vendor: "Vendor", part_no: Union[List[str], str]) -> Optional["ObjectModel"]:
        """
        Get ObjectModel by part part_no,
        Search order:
            * NOC model name
            * asset.part_no* value (Part numbers)
            * asset.order_part_no* value (FRU numbers)
        """
        if isinstance(part_no, list):
            for p in part_no:
                m = cls._get_model(vendor, p)
                if m:
                    return m
            return None
        else:
            return cls._get_model(vendor, part_no)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_model_cache"), lock=lambda _: id_lock)
    def _get_model(cls, vendor: "Vendor", part_no: str) -> Optional["ObjectModel"]:
        """
        Get ObjectModel by part part_no,
        Search order:
            * NOC model name
            * asset.part_no* value (Part numbers)
            * asset.order_part_no* value (FRU numbers)
        """
        # Check for model name
        if " | " in part_no:
            m = ObjectModel.objects.filter(name=part_no).first()
            if m:
                return m
        # Check for asset_part_no
        m = ObjectModel.objects.filter(
            vendor=vendor.id,
            data__match={"interface": "asset", "attr": "part_no", "value": part_no},
        ).first()
        if m:
            return m
        m = ObjectModel.objects.filter(
            vendor=vendor.id,
            data__match={"interface": "asset", "attr": "order_part_no", "value": part_no},
        ).first()
        if m:
            return m
        # Not found
        # Fallback and search by unique part no
        oml = list(
            ObjectModel.objects.filter(
                data__match={"interface": "asset", "attr": "part_no", "value": part_no}
            )
        )
        if len(oml) == 1:
            # Unique match found
            return oml[0]
        oml = list(
            ObjectModel.objects.filter(
                data__match={"interface": "asset", "attr": "order_part_no", "value": part_no}
            )
        )
        if len(oml) == 1:
            # Unique match found
            return oml[0]
        # Nothing found
        return None

    def get_outer(self) -> Optional[ObjectModelConnection]:
        """
        Get outer connection if any.
        """
        for c in self.connections:
            if c.is_outer:
                return c
        return None

    @property
    def json_data(self) -> dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "vendor__code": self.vendor.code[0],
            "data": [c.json_data for c in self.data],
            "connections": [c.json_data for c in self.connections],
        }
        if self.short_label:
            r["short_label"] = self.short_label
        if self.glyph:
            r["glyph__name"] = self.glyph.name
        if self.cross:
            r["cross"] = [s.json_data for s in self.cross]
        if self.sensors:
            r["sensors"] = [s.json_data for s in self.sensors]
        if self.connection_rule:
            r["connection_rule__name"] = self.connection_rule.name
        if self.configuration_rule:
            r["configuration_rule__name"] = self.configuration_rule.name
        if self.cr_context:
            r["cr_context"] = self.cr_context
        if self.modes:
            r["modes"] = [s.json_data for s in self.modes]
        if self.plugins:
            r["plugins"] = self.plugins
        if self.front_facade:
            r["front_facade__name"] = self.front_facade.name
        if self.rear_facade:
            r["rear_facade__name"] = self.rear_facade.name
        if self.labels:
            r["labels"] = self.labels
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "vendor__code",
                "description",
                "connection_rule__name",
                "cr_context",
                "plugins",
                "labels",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        print(p)
        return os.path.join(*p) + ".json"

    def clear_unknown_models(self):
        """
        Exclude model's part numbers from unknown models
        """
        part_no = (self.get_data("asset", "part_no") or []) + (
            self.get_data("asset", "order_part_no") or []
        )
        if part_no:
            vendor = self.vendor
            if isinstance(vendor, str):
                vendor = Vendor.get_by_id(vendor)
            UnknownModel.clear_unknown(vendor.code, part_no)

    def iter_effective_labels(self):
        return []

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_objectmodel")

    def iter_next_connections(self, start: str, n: int) -> Iterable[ObjectModelConnection]:
        """
        Iterate up to n compatible next connections.

        Connections will be compatible with `start`.

        Attributes:
            start: Starting connection name.
            n: Amount of next connections.

        Returns:
            Yields connection objects.
        """
        scn: Optional[ObjectModelConnection] = None
        for cn in self.connections:
            # Wait for start
            if not scn:
                if cn.name == start:
                    scn = cn
                continue
            # Check compatibility
            # @todo: Consider compatible types
            if not (
                cn.direction == scn.direction
                and cn.gender == scn.gender
                and cn.type.id == scn.type.id
            ):
                return
            # Compatible
            yield cn
            n -= 1
            # Check for finish
            if not n:
                return

    @property
    def glyph_css_class(self) -> Optional[str]:
        # Explicitly defined glyph
        if self.glyph:
            return self.glyph.css_class
        # Pre-defined glyphs
        # Rack
        if self.get_data("rack", "units"):
            return "fa fa-th-large"
        # Chassis
        if self.cr_context == "CHASSIS":
            return "fa fa-square"
        # Linecard
        if self.cr_context == "LINECARD":
            return "fa fa-window-minimize"
        # Transceiver
        if self.cr_context == "XCVR":
            return "fa fa-bolt"
        return None

    def _ensure_connection_names(self):
        """
        Ensure objects with this models have no hanging connections.
        """
        from .object import Object
        from .objectconnection import ObjectConnection

        # Get affected objects
        obj_ids = {
            doc["_id"] for doc in Object._get_collection().find({"model": self.id}, {"_id": 1})
        }
        if not obj_ids:
            return  # No objects

        # Find affected connections
        to_prune_connections = set()
        cable_candidates = set()
        valid_names = {c.name for c in self.connections}
        for oc in ObjectConnection._get_collection().find(
            {
                "connection": {
                    "$elemMatch": {
                        "object": {"$in": list(obj_ids)},
                        "name": {"$nin": list(valid_names)},
                    }
                }
            }
        ):
            conn_id = oc["_id"]
            conns = oc.get("connection")
            if len(conns) == 1:
                to_prune_connections.add(conn_id)
                continue
            if len(conns) > 2:
                conns = [
                    cc for cc in conns if cc["object"] not in obj_ids or cc["name"] in valid_names
                ]
                if len(conns) > 1:
                    ...  # @todo: Update connections
                else:
                    to_prune_connections.add(conn_id)
                continue
            # Connection is broken
            to_prune_connections.add(conn_id)
            # Potencial cables
            cable_candidates.add([cc["object"] for cc in conns if cc["object"] not in obj_ids][0])
        # Process cables
        if cable_candidates:
            to_prune_objects = {
                obj.id
                for obj in Object.objects.filter(id__in=list(cable_candidates))
                if obj.is_wire
            }
            if to_prune_objects:
                to_prune_connections.update(
                    doc["_id"]
                    for doc in ObjectConnection._get_collection().find(
                        {"connection.object": {"$in": list(to_prune_objects)}}, {"_id": 1}
                    )
                )
                Object._get_collection().delete_many({"_id": {"$in": list(to_prune_objects)}})
        if to_prune_connections:
            ObjectConnection._get_collection().delete_many(
                {"_id": {"$in": list(to_prune_connections)}}
            )

    def get_default_mode(self) -> str | None:
        """
        Get default mode for model.

        Returns:
            Mode name if present, or None.
        """
        if self.modes:
            for mi in self.modes:
                if mi.is_default:
                    return mi.name
        return None


class ModelConnectionsCache(Document):
    meta = {
        "collection": "noc.inv.objectconnectionscache",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["model", ("type", "gender")],
    }
    # Connection type
    type = ObjectIdField()
    gender = StringField(choices=["s", "m", "f"])
    model = ObjectIdField()
    name = StringField()

    @classmethod
    def rebuild(cls):
        """
        Rebuild cache
        """
        nc = []
        for m in ObjectModel.objects.all():
            for c in m.connections:
                nc += [{"type": c.type.id, "gender": c.gender, "model": m.id, "name": c.name}]
        collection = ModelConnectionsCache._get_collection()
        collection.drop()
        if nc:
            collection.insert(nc)

    @classmethod
    def update_for_model(cls, model: "ObjectModel"):
        """
        Update connection cache for object model
        :param model: ObjectModel instance
        :return:
        """
        cache = {}
        collection = ModelConnectionsCache._get_collection()
        for cc in ModelConnectionsCache.objects.filter(model=model.id):
            cache[(cc.type, cc.gender, cc.model, cc.name)] = cc.id
        bulk = []
        for c in model.connections:
            k = (c.type.id, c.gender, model.id, c.name)
            if k in cache:
                del cache[k]
                continue
            bulk += [
                InsertOne(
                    {"type": c.type.id, "gender": c.gender, "model": model.id, "name": c.name}
                )
            ]
        if cache:
            bulk += [DeleteOne({"_id": x}) for x in cache.values()]
        if bulk:
            collection.bulk_write(bulk)
