# ---------------------------------------------------------------------
# ObjectModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
import re
from typing import Any, Dict, Optional, List, Tuple, Union

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    UUIDField,
    DictField,
    ListField,
    EmbeddedDocumentField,
    ObjectIdField,
)
from mongoengine.errors import ValidationError
import cachetools
from pymongo import InsertOne, DeleteOne

# NOC modules
from noc.main.models.doccategory import category
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.change.decorator import change
from noc.pm.models.measurementunits import MeasurementUnits
from .connectiontype import ConnectionType
from .connectionrule import ConnectionRule
from .unknownmodel import UnknownModel
from .vendor import Vendor

id_lock = Lock()

rx_composite_pins_validate = re.compile(r"\d+\-\d+")


class ObjectModelConnection(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    description = StringField()
    type = PlainReferenceField(ConnectionType)
    direction = StringField(choices=["i", "o", "s"])  # Inner slot  # Outer slot  # Connection
    gender = StringField(choices=["s", "m", "f"])
    combo = StringField(required=False)
    group = StringField(required=False)
    cross = StringField(required=False)
    protocols = ListField(StringField(), required=False)
    internal_name = StringField(required=False)
    composite = StringField(required=False)
    composite_pins = StringField(required=False)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.description == other.description
            and self.type.id == other.type.id
            and self.direction == other.direction
            and self.gender == other.gender
            and self.combo == other.combo
            and self.group == other.group
            and self.cross == other.cross
            and self.protocols == other.protocols
            and self.internal_name == other.internal_name
            and self.composite == other.composite
            and self.composite_pins == other.composite_pins
        )

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "description": self.description,
            "type__name": self.type.name,
            "direction": self.direction,
            "gender": self.gender,
        }
        if self.combo:
            r["combo"] = self.combo
        if self.group:
            r["group"] = self.group
        if self.cross:
            r["cross"] = self.cross
        if self.protocols:
            r["protocols"] = self.protocols
        if self.internal_name:
            r["internal_name"] = self.internal_name
        if self.composite:
            r["composite"] = self.composite
        if self.composite_pins:
            r["composite_pins"] = self.composite_pins
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
    def json_data(self) -> Dict[str, Any]:
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
            ("vendor", "data.asset.part_no"),
            ("vendor", "data.asset.order_part_no"),
            "labels",
            "effective_labels",
        ],
        "json_collection": "inv.objectmodels",
        "json_unique_fields": ["name", "uuid"],
        "json_depends_on": ["inv.vendors", "inv.connectionrules", "pm.measurementunits"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    vendor = PlainReferenceField(Vendor)
    connection_rule = PlainReferenceField(ConnectionRule, required=False)
    # Connection rule context
    cr_context = StringField(required=False)
    data = DictField()
    connections = ListField(EmbeddedDocumentField(ObjectModelConnection))
    sensors = ListField(EmbeddedDocumentField(ObjectModelSensor))
    plugins = ListField(StringField(), required=False)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _model_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["ObjectModel"]:
        return ObjectModel.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["ObjectModel"]:
        return ObjectModel.objects.filter(name=name).first()

    def get_data(self, interface: str, key: str):
        v = self.data.get(interface, {})
        return v.get(key)

    def on_save(self):
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

    def get_connection_proposals(self, name: str) -> List[Tuple["ObjectModel", str]]:
        """
        Return possible connections for connection name
        as (model id, connection name)
        """
        cn = self.get_model_connection(name)
        if not cn:
            return []  # Connection not found
        r = []
        c_types = cn.type.get_compatible_types(cn.gender)
        og = ConnectionType.OPPOSITE_GENDER[cn.gender]
        for cc in ModelConnectionsCache.objects.filter(type__in=c_types, gender=og):
            r += [(cc.model, cc.name)]
        return r

    def get_model_connection(self, name: str) -> Optional["ObjectModelConnection"]:
        for c in self.connections:
            if c.name == name or (c.internal_name and c.internal_name == name):
                return c
        return None

    def check_connection(
        self,
        lc: "ObjectModelConnection",
        rc: "ObjectModelConnection",
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
        m = ObjectModel.objects.filter(vendor=vendor.id, data__asset__part_no=part_no).first()
        if m:
            return m
        m = ObjectModel.objects.filter(vendor=vendor.id, data__asset__order_part_no=part_no).first()
        if m:
            return m
        # Not found
        # Fallback and search by unique part no
        oml = list(ObjectModel.objects.filter(data__asset__part_no=part_no))
        if len(oml) == 1:
            # Unique match found
            return oml[0]
        oml = list(ObjectModel.objects.filter(data__asset__order_part_no=part_no))
        if len(oml) == 1:
            # Unique match found
            return oml[0]
        # Nothing found
        return None

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "vendor__code": self.vendor.code[0],
            "data": self.data,
            "connections": [c.json_data for c in self.connections],
        }
        if self.sensors:
            r["sensors"] = [s.json_data for s in self.sensors]
        if self.connection_rule:
            r["connection_rule__name"] = self.connection_rule.name
        if self.cr_context:
            r["cr_context"] = self.cr_context
        if self.plugins:
            r["plugins"] = self.plugins
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
        return os.path.join(*p) + ".json"

    def clear_unknown_models(self):
        """
        Exclude model's part numbers from unknown models
        """
        if "asset" in self.data:
            part_no = self.data["asset"].get("part_no", []) + self.data["asset"].get(
                "order_part_no", []
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
