# ---------------------------------------------------------------------
# ModelInterface model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from typing import Optional, Any
from pathlib import Path

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, UUIDField, EmbeddedDocumentListField
import cachetools

# NOC modules
from .error import ModelDataError
from noc.core.copy import deep_copy
from noc.core.escape import json_escape as q
from noc.core.validators import is_objectid
from noc.sa.interfaces.base import (
    StringParameter,
    BooleanParameter,
    FloatParameter,
    IntParameter,
    StringListParameter,
)
from noc.core.path import safe_json_path

id_lock = Lock()


T_MAP = {
    "str": StringParameter(),
    "int": IntParameter(),
    "float": FloatParameter(),
    "bool": BooleanParameter(),
    "strlist": StringListParameter(),
}

A_TYPE = ["str", "int", "float", "bool", "objectid", "ref", "strlist"]


class ModelInterfaceAttr(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    type = StringField(choices=[(t, t) for t in A_TYPE])
    description = StringField()
    required = BooleanField(default=False)
    is_const = BooleanField(default=False)
    # default
    # ref

    def __str__(self):
        return self.name

    def __eq__(self, v):
        return (
            self.name == v.name
            and self.type == v.type
            and self.description == v.description
            and self.required == v.required
            and self.is_const == v.is_const
        )

    def _clean(self, value):
        return getattr(self, f"clean_{self.type}")(value)

    def clean_str(self, value):
        return value

    def clean_int(self, value):
        return int(value)

    def clean_float(self, value):
        if isinstance(value, str):
            return float(value.replace(",", "."))
        return float(value)

    def clean_bool(self, value):
        value = value.lower()
        if value in ("yes", "y", "t", "true"):
            return True
        try:
            v = int(value)
            return v != 0
        except ValueError:
            return False

    def clean_objectid(self, value):
        value = value.lower()
        if is_objectid(value):
            return value
        raise ValueError(f"Value {value} is not ObjectID")

    def clean_strlist(self, value):
        if isinstance(value, str):
            return value.split(",")
        return value


class ModelInterface(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.modelinterfaces",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.modelinterfaces",
        "json_unique_fields": ["uuid", "name"],
    }

    name = StringField(unique=True)
    description = StringField()
    attrs = EmbeddedDocumentListField(ModelInterfaceAttr)
    uuid = UUIDField(binary=True)

    _id_cache = cachetools.TTLCache(100, 10)
    _name_cache = cachetools.TTLCache(100, 10)
    _attr_cache = cachetools.TTLCache(1000, 10)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: str | ObjectId) -> Optional["ModelInterface"]:
        return ModelInterface.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["ModelInterface"]:
        return ModelInterface.objects.filter(name=name).first()

    def get_attr(self, name: str) -> ModelInterfaceAttr | None:
        for a in self.attrs:
            if a.name == name:
                return a
        return None

    def to_json(self) -> str:
        ar = []
        for a in self.attrs:
            r = ["        {"]
            r.append(f'            "name": "{q(a.name)}",')
            r.append(f'            "type": "{q(a.type)}",')
            r.append(f'            "description": "{q(a.description)}",')
            r.append(f'            "required": {q(a.required)},')
            r.append(f'            "is_const": {q(a.is_const)}')
            r.append("        }")
            ar.append("\n".join(r))
        r = [
            "{",
            f'    "name": "{q(self.name)}",',
            f'    "$collection": "{self._meta["json_collection"]}",',
            f'    "uuid": "{self.uuid!s}",',
            f'    "description": "{q(self.description)}",',
            '    "attrs": [',
            ",\n".join(ar),
            "    ]",
            "}",
        ]
        return "\n".join(r) + "\n"

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    @classmethod
    def clean_data(cls, data: list[dict[str, str]]) -> list[dict[str, Any]]:
        """
        Convert types according to interface
        """
        r = []
        for item in data:
            item = deep_copy(item)
            interface = item["interface"]
            mi = ModelInterface.get_by_name(interface)
            if not mi:
                raise ModelDataError(f"Unknown interface '{interface}'")
            a = mi.get_attr(item["attr"])
            vv = item["value"]
            if a.type == "strlist":
                if isinstance(vv, str):
                    vv = [vv]
                y = set()
                for x in vv:
                    y.update(x.split(","))
                vv = [x.strip() for x in sorted(y) if x.strip()]
            item["value"] = T_MAP[a.type].clean(vv)
            r.append(item)
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_attr_cache"), lock=lambda _: id_lock)
    def get_interface_attr(cls, interface: str, key: str) -> "ModelInterfaceAttr":
        mi = ModelInterface.objects.filter(name=interface).first()
        if not mi:
            raise ModelDataError(f"Invalid interface '{interface}'")
        attr = mi.get_attr(key)
        if not attr:
            raise ModelDataError(f"Invalid attribute '{interface}.{key}'")
        return attr
