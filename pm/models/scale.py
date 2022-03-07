# ----------------------------------------------------------------------
# Scale model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Any, Dict, Optional
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check


id_lock = Lock()


@on_delete_check(check=[("pm.MetricType", "scale")])
class Scale(Document):
    meta = {
        "collection": "scales",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.scales",
        "json_unique_fields": ["name", "code"],
    }

    # Unique units name
    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    # Unique addressable code
    code = StringField(unique=True)
    # Display label
    label = StringField()
    # Exponent base
    base = IntField(default=10)
    # Exponent
    exp = IntField(default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["Scale"]:
        return Scale.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["Scale"]:
        return Scale.objects.filter(code=code).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "code": self.code,
            "label": self.label,
            "base": self.base,
            "exp": self.exp,
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "code",
                "label",
                "base",
                "exp",
            ],
        )

    def get_json_path(self) -> str:
        return f"{quote_safe_path(self.name)}.json"
