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
from typing import List, Optional

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    EmbeddedDocumentListField,
)
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.ip import IP
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.sa.interfaces.base import StringParameter, IntParameter, BooleanParameter
from noc.pm.models.metrictype import MetricType
from .configurationscope import ConfigurationScope


id_lock = threading.Lock()


class IPParameter(object):
    def clean(self, value):
        return IP.prefix(value)


TYPE_MAP = {
    "str": StringParameter(),
    "int": IntParameter(),
    "bool": BooleanParameter(),
    "ip": IPParameter(),
}


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
    id = StringField()
    name = StringField()

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class ParamSchemaItem(EmbeddedDocument):
    meta = {"strict": False}
    key = StringField(
        choices=["maximum", "minimum", "maxLength", "minLength", "pattern", "step"], required=True
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


class ConfigurationParam(Document):
    meta = {
        "collection": "configurationparams",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "cm.configurationparams",
        "json_unique_fields": ["code", "uuid"],
    }

    name = StringField(unique=True)
    code = StringField(unique=True)
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
    threshold_type = StringField()
    metric_type: Optional["MetricType"] = PlainReferenceField(MetricType, required=False)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ConfigurationParam.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code):
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
                "description",
                "source",
                "params",
            ],
        )

    def get_parameter(self):
        return TYPE_MAP[self.type]
