# ---------------------------------------------------------------------
# MetricType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
from threading import Lock
from typing import Any, Dict, Callable, Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    ObjectIdField,
    LongField,
    ListField,
    BooleanField,
    ReferenceField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.base import NULLIFY
from mongoengine.errors import ValidationError
import cachetools

# NOC Modules
from noc.config import config
from noc.core.mongo.fields import PlainReferenceField
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json
from noc.core.defer import call_later
from noc.core.model.decorator import on_save, on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.expr import get_vars
from noc.main.models.doccategory import category
from noc.inv.models.capability import Capability
from .metricscope import MetricScope
from .measurementunits import MeasurementUnits
from .scale import Scale


id_lock = Lock()


class AgentMappingItem(EmbeddedDocument):
    collector = StringField()
    field = StringField()

    def __str__(self):
        return f"{self.collector}.{self.field}"

    def json_data(self) -> Dict[str, Any]:
        return {"collector": self.collector, "field": self.field}


@on_save
@change
@bi_sync
@on_delete_check(
    check=[
        ("sa.ManagedObjectProfile", "metrics__metric_type"),
        ("cm.ConfigurationParam", "metric_type"),
        ("inv.InterfaceProfile", "metrics__metric_type"),
        ("sla.SLAProfile", "metrics__metric_type"),
        ("pm.MetricAction", "compose_inputs__metric_type"),
        ("pm.MetricAction", "compose_metric_type"),
    ]
)
@category
class MetricType(Document):
    meta = {
        "collection": "noc.metrictypes",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.metrictypes",
        "json_depends_on": ["pm.metricscopes"],
        "json_unique_fields": ["name"],
    }

    # Metric type name, i.e. Interface | Load | In
    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    # Metric scope reference
    scope: "MetricScope" = PlainReferenceField(MetricScope)
    # Database field name
    field_name = StringField()
    # Database field type
    field_type = StringField(
        choices=[
            ("UInt8", "UInt8"),
            ("Int8", "Int8"),
            ("UInt16", "UInt16"),
            ("Int16", "Int16"),
            ("UInt32", "UInt32"),
            ("Int32", "Int32"),
            ("UInt64", "UInt64"),
            ("Int64", "Int64"),
            ("Float32", "Float32"),
            ("Float64", "Float64"),
            ("String", "String"),
        ]
    )
    # Text description
    description = StringField(required=False)
    # Measurement units
    units = PlainReferenceField(
        MeasurementUnits, default=MeasurementUnits.get_default_measurement_units
    )
    # Scale
    scale: "Scale" = PlainReferenceField(Scale, default=Scale.get_default_scale)
    # Metric is delta scale
    is_delta = BooleanField(default=False)
    # Measure name, like 'kbit/s'
    # Compatible to Grafana
    measure = StringField()
    # Compose expression
    compose_inputs = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
    compose_expression = StringField()
    # Agent mappings
    agent_mappings = EmbeddedDocumentListField(AgentMappingItem)
    # Optional required capability
    required_capability = PlainReferenceField(Capability)
    # Object id in BI, used for counter context hashing
    bi_id = LongField(unique=True)
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=200, ttl=300)
    _name_cache = cachetools.TTLCache(maxsize=200, ttl=300)
    _field_cache = cachetools.TTLCache(maxsize=200, ttl=300)
    _bi_id_cache = cachetools.TTLCache(maxsize=200, ttl=300)

    def __str__(self):
        return self.name

    @property
    def is_compose(self) -> bool:
        return bool(self.compose_expression)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "scope__name": self.scope.name,
            "field_name": self.field_name,
            "field_type": self.field_type,
            "description": self.description,
            "measure": self.measure,
            "units__code": self.units.code,
            "scale__code": self.scale.code,
        }
        if self.agent_mappings:
            r["agent_mappings"] = [m.json_data() for m in self.agent_mappings]
        if self.required_capability:
            r["required_capability__name"] = self.required_capability.name
        if self.compose_expression:
            r["compose_expression"] = self.compose_expression
            r["compose_inputs__name"] = [mt.name for mt in self.compose_inputs]
        if self.is_delta:
            r["is_delta"] = self.is_delta
        return r

    def clean(self):
        if self.compose_inputs and self in self.compose_inputs:
            raise ValidationError({"compose_inputs": "Not allowed same in Compose Metrics"})
        if self.compose_expression:
            try:
                metric_fields = get_vars(self.compose_expression)
            except Exception as e:
                raise ValidationError({"compose_expression": str(e)})
            for m_f in metric_fields:
                mt = MetricType.get_by_field_name(m_f)
                if m_f == "time_delta":
                    continue
                if not mt or mt not in self.compose_inputs:
                    raise ValidationError(
                        {"compose_expression": f"Unknown variable {m_f} on expression"}
                    )

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "scope__name",
                "field_name",
                "field_type",
                "description",
                "measure",
                "units__code",
                "scale__code",
                "agent_mappings",
                "required_capability__name",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MetricType"]:
        return MetricType.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["MetricType"]:
        return MetricType.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_field_cache"), lock=lambda _: id_lock)
    def get_by_field_name(cls, fname, scope: Optional[str] = None) -> Optional["MetricType"]:
        if scope:
            scope = MetricScope.get_by_table_name(scope)
            return MetricType.objects.filter(field_name=fname, scope=scope).first()
        return MetricType.objects.filter(field_name=fname).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["MetricType"]:
        return MetricType.objects.filter(bi_id=bi_id).first()

    def on_save(self):
        call_later(
            "noc.core.clickhouse.ensure.ensure_all_pm_scopes", scheduler="scheduler", delay=30
        )

    def clean_value(self, value):
        return getattr(self, f"clean_{self.field_type}")(value)

    def get_cleaner(self) -> Callable:
        return getattr(self, f"clean_{self.field_type}", None)

    @staticmethod
    def clean_UInt8(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 255:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int8(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -127 or v > 127:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt16(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 65535:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int16(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -32767 or v > 32767:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt32(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 4294967295:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int32(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -2147483647 or v > 2147483647:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt64(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 18446744073709551615:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int64(value) -> int:
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -9223372036854775807 or v > 9223372036854775807:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Float32(value) -> float:
        return float(value)

    @staticmethod
    def clean_Float64(value) -> float:
        return float(value)

    @staticmethod
    def clean_String(value) -> str:
        return str(value)

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmetrics:
            yield "cfgmetrics", self.id
