# ----------------------------------------------------------------------
# MeasurementUnits document model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Any, Dict, Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, UUIDField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.expr import get_fn
from noc.pm.models.scale import Scale

DEFAULT_UNITS_NAME = "Scalar"

id_lock = Lock()


class ConvertFrom(EmbeddedDocument):
    # Unit code
    unit = PlainReferenceField("pm.MeasurementUnits")
    # Expression to convert from other unit
    expr = StringField()

    def __str__(self):
        return self.unit

    def clean(self):
        try:
            get_fn(self.expr)
        except SyntaxError:
            raise ValidationError("Expression syntax error")

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "unit__code": self.unit.code,
            "expr": self.expr,
        }


class EnumValue(EmbeddedDocument):
    key = StringField()
    value = IntField()

    def __str__(self):
        return f"{self.key}: {self.value}"

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"key": self.key, "value": self.value}


@on_delete_check(
    check=[
        ("inv.Sensor", "units"),
        ("inv.SensorProfile", "units"),
        ("pm.MetricType", "units"),
        ("pm.MeasurementUnits", "base_unit"),
        ("pm.MeasurementUnits", "convert_from.unit"),
    ]
)
class MeasurementUnits(Document):
    meta = {
        "collection": "measurementunits",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.measurementunits",
        "json_unique_fields": ["name"],
    }

    # Unique units name
    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    # Addressable code
    code = StringField(unique=True)
    # Base unit, for alternate ones
    base_unit = PlainReferenceField("self", null=True)
    # Optional description
    description = StringField()
    # Short label
    label = StringField()
    # Label for dashboards
    # Compatible to Grafana, like 'kbit/s'
    dashboard_label = StringField(required=False)
    dashboard_sr_color = IntField(default=0x000000, required=False, null=True)
    # Conversion rules
    convert_from = ListField(EmbeddedDocumentField(ConvertFrom))
    # Enumerations
    enum = ListField(EmbeddedDocumentField(EnumValue))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_MU_NAME = "Scalar"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MeasurementUnits"]:
        return MeasurementUnits.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["MeasurementUnits"]:
        return MeasurementUnits.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["MeasurementUnits"]:
        return MeasurementUnits.objects.filter(code=code).first()

    @classmethod
    def get_default_measurement_units(cls) -> "MeasurementUnits":
        return MeasurementUnits.objects.filter(name=cls.DEFAULT_MU_NAME).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "code": self.code,
            "label": self.label,
            "dashboard_label": self.dashboard_label,
        }
        if self.base_unit:
            r["base_unit__code"] = self.base_unit.code
        if self.dashboard_sr_color:
            r["dashboard_sr_color"] = self.dashboard_sr_color
        if self.description:
            r["description"] = self.description
        if self.convert_from:
            r["convert_from"] = [x.json_data for x in self.convert_from]
        if self.enum:
            r["enum"] = [x.json_data for x in self.enum]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "code",
                "base_unit__code",
                "description",
                "label",
                "dashboard_label",
                "base_unit__code",
                "dashboard_sr_color",
                "convert_from",
                "enum",
            ],
        )

    def get_json_path(self) -> str:
        return f"{quote_safe_path(self.name)}.json"

    def humanize(self, value: Union[float, int]) -> str:
        if self.code == "1":
            return str(value)
        elif self.code == "s":
            return Scale.humanize_time(value)
        elif self.code == "bit/s" or self.code == "pps":
            return Scale.humanize_speed(value)
        return "%s %s" % Scale.humanize(value)
