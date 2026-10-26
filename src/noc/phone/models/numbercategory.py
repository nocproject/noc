# ---------------------------------------------------------------------
# NumberCategory model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Future imports
from __future__ import annotations

# Python modules
import operator
import re
from threading import Lock

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import BooleanField, EmbeddedDocumentListField, IntField, StringField

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import PlainReferenceField

from .dialplan import DialPlan

id_lock = Lock()


class NumberCategoryRule(EmbeddedDocument):
    dialplan = PlainReferenceField(DialPlan)
    mask = StringField()
    is_active = BooleanField()
    description = StringField()


@on_delete_check(check=[("phone.PhoneNumber", "category")])
class NumberCategory(Document):
    meta = {"collection": "noc.numbercategories", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    order = IntField(default=1000)
    rules = EmbeddedDocumentListField(NumberCategoryRule)

    _id_cache = cachetools.TTLCache(100, ttl=60)
    _rule_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: str | ObjectId) -> NumberCategory | None:
        return NumberCategory.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"), lock=lambda _: id_lock)
    def get_rules(cls):
        r = []
        for nc in NumberCategory.objects.filter(is_active=True).order_by("order"):
            for rule in nc.rules:
                if not rule.is_active:
                    continue
                r.append((rule.dialplan, re.compile(rule.mask), nc))
        return r
