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
    EnumField,
    UUIDField,
    LongField,
    IntField,
)
from bson import ObjectId

# NOC modules
from noc.core.model.decorator import on_delete_check, tree
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json
from noc.core.models.valuetype import VariableType

id_lock = Lock()


class Resource(EmbeddedDocument):
    """
    System Resources for Category
    Attributes:
        code: Resource Code
        extend_path: Extend path by resolve Resource
        oper_status: Update Oper Status on resource
    """

    meta = {"strict": False}

    code: str = StringField(
        required=True, choices=[("if", "Interface"), ("si", "SubInterface"), ("ip", "Address")]
    )
    extend_path = BooleanField(default=False)  # Append Resource Path
    oper_status: bool = StringField(choices=[("UP", "Up"), ("DOWN", "Down")], required=False)

    @property
    def json_data(self):
        return {
            "name": self.code,
            "required": self.extend_path,
            "match_suppress": self.oper_status,
        }


class EventCategoryVar(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField(required=True)
    description = StringField(required=False)
    type: VariableType = EnumField(VariableType, required=True)
    required = BooleanField(required=True)
    # managed_object map ?
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
        is_unique: Only one category on Event (on parent)
        vars: Variables description
        suppression_policy: Policy that suppress received event by vars
            * C - only changed variables
            * D - supress by timer if equal variables
        object_scope: Object search scope
            * D - Disable Target (Info Category)
            * O - Object
            * M - Managed Object
        object_resolver: How object find
            * Disable - for information only Classes
            * By Profile - By Profile method
            * By Source - By Target mappings
        managed_object_required: Mapping Is Required, if not - dropped message
        include_object_paths: Add object paths to paths field
        oper_status: Update oper status on Object
        resources: Resource Map rules
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
        choices=[("C", "Changed"), ("D", "Duplicated")], default="D"
    )
    suppression_window = IntField(default=0)
    resources: List["Resource"] = EmbeddedDocumentListField(Resource)
    # Object Resolve
    object_scope: str = StringField(
        choices=[
            ("D", "Disable"),
            ("O", "Object"),
            ("M", "ManagedObject"),
            # CPE
        ],
        default="M",
    )
    # If not mapped - event dropped
    managed_object_required: bool = BooleanField(default=True)
    object_resolver: str = StringField(
        choices=[("P", "By Profile"), ("T", "By Target")], default="T"
    )
    include_object_paths: str = BooleanField(default=True)
    oper_status: bool = StringField(choices=[("UP", "Up"), ("DOWN", "Down")], required=False)
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
            "suppression_policy": self.suppression_policy,
            "suppression_window": self.suppression_window,
            "object_scope": self.object_scope,
            "managed_object_required": self.managed_object_required,
            "include_object_paths": self.include_object_paths,
            "object_resolver": self.object_resolver,
            "vars": [vv.json_data for vv in self.vars],
            "resources": [r.json_data for r in self.resources],
        }
        if self.parent:
            r["parent__name"] = self.parent.name
        if self.oper_status:
            r["oper_status"] = self.oper_status
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "parent",
                "description",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def get_rule_config(cls, category: "EventCategory"):
        """Build Category Rules"""
        from noc.fm.models.dispositionrule import DispositionRule

        r = {
            "id": str(category.id),
            "name": category.name,
            "bi_id": str(category.bi_id),
            "is_unique": category.is_unique,
            "suppression_policy": category.suppression_policy,
            "suppression_window": category.suppression_window,
            "vars": [],
            "object_map": {
                "scope": category.object_scope,
                "managed_object_required": category.managed_object_required,
                "include_path": category.include_object_paths,
            },
            "handlers": [],
            "actions": [],
        }
        if category.oper_status:
            r["object_map"]["oper_status"] = category.oper_status == "UP"
        for vv in category.vars:
            r["vars"].append(
                {
                    "name": vv.name,
                    "type": vv.type.value,
                    "required": vv.required,
                    "match_suppress": vv.match_suppress,
                }
            )
        r["actions"] += DispositionRule.get_category_actions(category)
        return r
