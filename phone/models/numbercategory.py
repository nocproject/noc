# ---------------------------------------------------------------------
# NumberCategory model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
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
    rules = ListField(EmbeddedDocumentField(NumberCategoryRule))

    _id_cache = cachetools.TTLCache(100, ttl=60)
    _rule_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["NumberCategory"]:
        return NumberCategory.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"), lock=lambda _: id_lock)
    def get_rules(cls):
        r = []
        for nc in NumberCategory.objects.filter(is_active=True).order_by("order"):
            for rule in nc.rules:
                if not rule.is_active:
                    continue
                r += [(rule.dialplan, re.compile(rule.mask), nc)]
        return r
