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
from typing import Optional, Union, NamedTuple, Dict, Any, List

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


class Category(NamedTuple):
    level1: Optional["EventCategory"] = None
    level2: Optional["EventCategory"] = None
    level3: Optional["EventCategory"] = None


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


@tree(field="parent")
@bi_sync
@change
@on_delete_check()
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
    classified = BooleanField(default=False)
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

    @classmethod
    def from_string(cls, category: str) -> Category:
        """Convert dot-notation to category"""
        l1, l2, l3 = category.split(".")
        if l1:
            l1 = EventCategory.get_by_name(l1)
        if l2:
            l2 = EventCategory.get_by_name(l2)
        if l3:
            l3 = EventCategory.get_by_name(l2)
        return Category(level1=l1, level2=l2, level3=l3)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "level": self.level.value,
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

    # def save(self, *args, **kwargs):
    #     if " | " in self.name:
    #         p_name = " | ".join(self.name.split(" | ")[:-1])
    #         p = AlarmClassCategory.objects.filter(name=p_name).first()
    #         if not p:
    #             p = AlarmClassCategory(name=p_name)
    #             p.save()
    #         self.parent = p.id
    #     else:
    #         self.parent = None
    #     super().save(*args, **kwargs)
