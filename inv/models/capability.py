# ---------------------------------------------------------------------
# Capability model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
import operator
from threading import Lock
from typing import Any, Dict, Union, Optional, List

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    UUIDField,
    ObjectIdField,
    BooleanField,
    DictField,
    EnumField,
)

# NOC modules
from noc.main.models.doccategory import category
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path
from noc.core.model.decorator import on_delete_check
from noc.core.models.valuetype import ValueType, ARRAY_ANNEX

id_lock = Lock()

TCapsValue = Union[bool, str, int, float, List[Any]]


@on_delete_check(
    check=[
        ("pm.MetricType", "required_capability"),
        ("sa.Service", "caps__capability"),
        ("sa.ManagedObject", "caps__capability"),
        ("sa.CapsProfile", "caps__capability"),
        ("main.ModelTemplate", "params__set_capability"),
    ]
)
@category
class Capability(Document):
    meta = {
        "collection": "noc.inv.capabilities",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.capabilities",
        "json_unique_fields": ["name", "uuid"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    type: ValueType = EnumField(ValueType, required=True)
    allow_manual = BooleanField(default=False)
    multi = BooleanField(default=False)
    values = DictField(default=lambda: {}.copy())
    # Jinja2 template for managed object's card tags
    card_template = StringField(required=False)
    # Expose to agent, if set. Collector name
    agent_collector = StringField()
    # Collector param
    agent_param = StringField()
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Capability"]:
        return Capability.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Capability"]:
        return Capability.objects.filter(name=name).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "type": self.type.value,
            "card_template": self.card_template,
            "allow_manual": self.allow_manual,
            "multi": self.multi,
        }
        if self.agent_collector and self.agent_param:
            r["agent_collector"] = self.agent_collector
            r["agent_param"] = self.agent_param
        if self.values:
            r["values"] = dict(self.values)
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "type",
                "card_template",
                "agent_collector",
                "agent_param",
            ],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    def clean_value(self, v: TCapsValue) -> TCapsValue:
        """
        Clean caps value. Split to normalize for clean input value?
        For convert array (multiple) string, used ANNEX
        """
        if isinstance(v, str) and v.startswith(ARRAY_ANNEX):
            v = ValueType.convert_to_array(v[len(ARRAY_ANNEX) :])
        if self.multi and isinstance(v, list):
            return [self.type.clean_value(x) for x in v]
        if self.multi:
            return [self.type.clean_value(x) for x in ValueType.convert_to_array(str(v))]
        # if self.multi and not isinstance(v, str):
        #    raise ValueError("Value not convert to multiple")
        if not self.type:
            raise ValueError(f"Invalid type: {self.type}")
        return self.type.clean_value(v)

    def get_references(self, v: TCapsValue, scope: Optional[str] = None) -> List[str]:
        if self.multi and isinstance(v, list):
            return [
                self.type.clean_reference(x, scope)
                for x in v
                if self.type.clean_reference(x, scope)
            ]
        if not self.type:
            raise ValueError(f"Invalid type: {self.type}")
        r = self.type.clean_reference(v, scope)
        if r:
            return [r]
        return []

    def get_editor(self) -> Optional[Dict[str, Any]]:
        if not self.allow_manual:
            return None
        r = {"type": self.type.value, "multiple": self.multi, "choices": []}
        if self.values:
            r["type"] = "choices"
        for k in self.values:
            r["choices"].append(k)
        return r
