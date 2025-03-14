# ---------------------------------------------------------------------
# FM module Event Category models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import cachetools
import os
from threading import Lock
from typing import Optional, Union, Dict, Any, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    BooleanField,
    EmbeddedDocumentListField,
    UUIDField,
    EnumField,
    LongField,
)
from bson import ObjectId

# NOC modules
from noc.core.fm.enum import EventCategoryLevel
from noc.core.model.decorator import on_delete_check, tree
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

id_lock = Lock()


class EventCategoryVar(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField(required=True)
    description = StringField(required=False)
    type = StringField(
        required=True,
        choices=[
            (x, x)
            for x in (
                "str",
                "int",
                "float",
                "ipv4_address",
                "ipv6_address",
                "ip_address",
                "ipv4_prefix",
                "ipv6_prefix",
                "ip_prefix",
                "mac",
                "interface_name",
                "oid",
            )
        ],
    )
    required = BooleanField(required=True)
    match_suppress = BooleanField(default=False)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.description == other.description
            and self.type == other.type
            and self.required == other.required
            and self.match_suppress == other.match_suppress
        )

    @property
    def json_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required,
            "match_suppress": self.match_suppress,
        }


@tree(field="parent")
@bi_sync
@change
@on_delete_check(
    check=[("fm.EventClassificationRule", "categories"), ("fm.EventCategory", "parent")]
)
class EventCategory(Document):
    meta = {
        "collection": "noc.eventcategories",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.eventcategories",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    parent = ReferenceField("self", required=False)
    level: "EventCategoryLevel" = EnumField(EventCategoryLevel, required=True)
    vars: List["EventCategoryVar"] = EmbeddedDocumentListField(EventCategoryVar)
    # resources
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["EventCategory"]:
        return EventCategory.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["EventCategory"]:
        return EventCategory.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["EventCategory"]:
        return EventCategory.objects.filter(bi_id=bi_id).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "level": self.level.value,
            "vars": [vv.json_data for vv in self.vars],
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "level",
                "description",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
