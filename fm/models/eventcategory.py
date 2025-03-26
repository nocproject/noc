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
    LongField,
)
from bson import ObjectId

# NOC modules
from noc.core.model.decorator import on_delete_check, tree
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

id_lock = Lock()


class Resource(EmbeddedDocument):
    """
    Attributes:
        code: Resource Code
        required_target: Require Resolve Target Object
        extend_path: Extend path by resolve Resource
        update_oper_status: Update Oper Status on resource
    """

    meta = {"strict": False}

    code: str = StringField(
        required=True, choices=[("if", "Interface"), ("si", "SubInterface"), ("ip", "Address")]
    )
    required_target: bool = BooleanField(default=True)
    extend_path = BooleanField(default=False)  # Append Resource Path
    update_oper_status: BooleanField(default=False)  # set_oper_status API


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
    """

    Attributes:
        target_scope: Target scope
        target_map_method: Search object method
            * By Profile - By Profile method
            * By Source - By Target mappings
        required_target: Mapping Is Required, if not - dropped message
        extend_path_targets: Add object paths to paths fields
        update_target_status: Update oper status on Target
    """

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
    is_unique = BooleanField(default=False)
    vars: List["EventCategoryVar"] = EmbeddedDocumentListField(EventCategoryVar)
    suppression_policy: str = StringField(
        choices=[("C", "changed"), ("D", "duplicated")], default="D"
    )
    resources: List["Resource"] = EmbeddedDocumentListField(Resource)
    # Target Mapping
    target_scope: str = StringField(choices=[("O", "Object"), ("M", "ManagedObject")], default="M")
    required_target: bool = BooleanField(default=False)
    # Target Scope
    target_map_method: str = StringField(
        choices=[("P", "By Profile"), ("S", "By Sources")], default="S"
    )
    # If not mapped - event dropped
    extend_path_targets: str = BooleanField(default=True)
    update_target_status: bool = BooleanField(default=False)
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
