# ----------------------------------------------------------------------
# ConfigurationParam model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Union, NoReturn, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    EmbeddedDocumentListField,
)
from pydantic import BaseModel
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.pm.models.metrictype import MetricType
from .configurationscope import ConfigurationScope


id_lock = threading.Lock()


class ParamSchema(BaseModel):
    type: str  # number, string, bool
    # String Schema
    pattern: Optional[str] = None
    format: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    # Number Schema
    min: Optional[float] = None
    max: Optional[float] = None
    recommended_min: Optional[float] = None
    recommended_max: Optional[float] = None
    step: Optional[float] = None
    decimal: Optional[int] = None  # Choices 0, 0.1, 0.01, 0.001, 0.0001
    recommended_choices: List[str] = None
    choices: List[str] = None

    def clean(self, value: str) -> Union[str, float, bool]:
        if self.type == "bool":
            return value in ("yes", "true")
        if self.type == "number":
            return self.clean_number(value)
        return self.clean_string(value)

    def clean_number(self, value: str) -> float:
        value, msg = float(value), ""
        if self.decimal:
            value = round(value, self.decimal)
        if self.min and value < self.min:
            msg = f"Value less than {value}"
        if self.max and value > self.max:
            msg = f"Value less than {value}"
        if msg:
            raise ValueError(msg)
        return value

    def clean_string(self, value: Any) -> str:
        if self.pattern:
            match = re.match(self.pattern, value)
            if match:
                raise ValueError("Value is not match pattern: %s" % value)
        return value

    def merge(self, schema: "ParamSchema") -> NoReturn: ...

    @property
    def json_schema(self):
        """
        Return JSON Schema
        """
        r = {}
        if self.type == "bool":
            return {}
        r["allowBlank"] = False
        if self.choices:
            return {"choices": self.choices}
        elif self.type == "string":
            r["minLength"] = self.min_length or 0
            r["maxLength"] = self.max_length or 100
            if self.pattern:
                r["regex"] = self.pattern
        elif self.type == "number":
            if self.min is not None:
                r["minValue"] = self.min
            if self.max is not None:
                r["maxValue"] = self.max
            if self.step:
                r["step"] = self.step
        return r


@dataclass
class ScopeVariant(object):
    scope: "ConfigurationScope"
    value: Optional[str] = None

    def __str__(self):
        return self.code

    @property
    def code(self):
        if not self.value:
            return self.scope.name
        return f"{self.scope.name}::{self.value}"

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other) -> bool:
        if self.scope.id != other.scope.id:
            return False
        if not self.value:
            return True
        return self.value == other.value

    @classmethod
    def from_code(cls, code: str) -> "ScopeVariant":
        scope, *v = code.split("::")
        s = ConfigurationScope.get_by_name(scope.strip("@"))
        if not s:
            ValueError("Unknown scope: %s" % scope)
        # check value by helper
        return ScopeVariant(s, v[0] if v else None)


@dataclass
class ParamData(object):
    code: str
    schema: ParamSchema
    scopes: Optional[List[ScopeVariant]] = None
    value: Optional[Any] = None

    def __str__(self) -> str:
        if self.scopes:
            return f"{self.code}@{self.scope} = {self.value}"
        return f"{self.code} = {self.value}"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def scope(self) -> str:
        return "".join(f"@{s.code}" for s in self.scopes)

    @property
    def param(self) -> "ConfigurationParam":
        return ConfigurationParam.get_by_code(self.code)


class ScopeItem(EmbeddedDocument):
    meta = {"strict": False}
    scope: "ConfigurationScope" = PlainReferenceField(ConfigurationScope, required=True)
    is_required = BooleanField(default=True)

    def __str__(self):
        return self.scope.name

    def to_json(self):
        return {
            "scope__name": self.scope.name,
            "is_required": self.is_required,
        }


class ConfigurationParamChoiceItem(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField()
    value = StringField()

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "name": self.name,
            "value": self.value,
        }


class ParamSchemaItem(EmbeddedDocument):
    meta = {"strict": False}
    key = StringField(
        choices=["max", "min", "max_length", "min_length", "pattern", "step", "decimal"],
        required=True,
    )
    format = StringField(choices=["date-time", "email", "ip", "uuid"], required=False)
    value = StringField(required=False)
    # Model Interface Reference
    model_interface = StringField()
    model_attr = StringField()

    def to_json(self):
        r = {
            "key": self.key,
            "value": self.value,
        }
        if self.format:
            r["format"] = self.format
        if self.model_interface and self.model_attr:
            r["model_interface"] = self.model_interface
            r["model_attr"] = self.model_attr
        return r


@on_delete_check(check=[("inv.Object", "cfg_data__param")])
class ConfigurationParam(Document):
    meta = {
        "collection": "configurationparams",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "cm.configurationparams",
        "json_unique_fields": ["code", "uuid"],
    }

    name = StringField(unique=True)
    code = StringField(unique=True, required=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    scopes: List["ScopeItem"] = EmbeddedDocumentListField(ScopeItem)
    # Int
    type: str = StringField(choices=["string", "number", "bool"], default="string")
    # Limitation
    schema: List["ParamSchemaItem"] = EmbeddedDocumentListField(ParamSchemaItem)
    #
    choices: List["ConfigurationParamChoiceItem"] = EmbeddedDocumentListField(
        ConfigurationParamChoiceItem
    )
    choices_scope: Optional["ConfigurationScope"] = PlainReferenceField(
        ConfigurationScope, required=False
    )
    # Threshold
    threshold_type = StringField(
        choices=["critical_min", "warning_min", "warning_max", "critical_max"]
    )
    metric_type: Optional["MetricType"] = PlainReferenceField(MetricType, required=False)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ConfigurationParam"]:
        return ConfigurationParam.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code) -> Optional["ConfigurationParam"]:
        return ConfigurationParam.objects.filter(code=code).first()

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def to_json(self) -> str:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "type": self.type,
            "code": self.code,
            "scopes": [s.to_json() for s in self.scopes],
        }
        if self.description:
            r["description"] = self.description
        if self.schema:
            r["schema"] = [s.to_json() for s in self.schema]
        if self.choices:
            r["choices"] = [c.to_json() for c in self.choices]
        if self.choices_scope:
            r["choices_scope__name"] = self.choices_scope.name
        if self.metric_type and self.threshold_type:
            r["threshold_type"] = self.threshold_type
            r["metric_type__name"] = self.metric_type.name
        return to_json(
            r,
            order=[
                "name",
                "$collection",
                "uuid",
                "code",
                "description",
                "scopes",
                "type",
                "choices",
            ],
        )

    def get_schema(self, o) -> ParamSchema:
        """
        Return param Schema
        """
        r = {"type": self.type}
        for si in self.schema:
            v = si.value
            if si.model_interface:
                v = o.model.get_data(si.model_interface, si.model_attr)
            r[si.key] = v
        if self.choices:
            r["choices"] = [c.name for c in self.choices]
        return ParamSchema(**r)

    @classmethod
    def clean_scope(cls, param: "ConfigurationParam", scope: str) -> str:
        """
        Clean parameter scopes from string
        """
        for s in scope.strip("@").split("@"):
            sv = ScopeVariant.from_code(s)
            if not param.has_scope(sv.scope.name):
                raise ValueError("Not supported scope '%s' on param: %s" % (s, param.code))
        if scope.startswith("@"):
            return scope
        return f"@{scope}"

    def has_scope(self, name: str) -> bool:
        """
        Check Param has scope
        :param name: Scope name
        """
        if not self.has_required_scopes:
            return True
        for s in self.scopes:
            if s.scope.name == name:
                return True
        return True

    @property
    def is_common(self) -> bool:
        """
        Param has Common Scope (without variant)
        """
        if not self.scopes:
            return True
        for s in self.scopes:
            if s.scope.is_common:
                return True
        return False

    @property
    def has_required_scopes(self) -> bool:
        return any(s for s in self.scopes if s.is_required)

    @property
    def threshold_op(self) -> Optional[str]:
        if not self.threshold_type:
            return None
        elif self.threshold_type.endswith("min"):
            return "<="
        return ">="
