# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NumberCategory model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, IntField,
                                ListField, EmbeddedDocumentField)
import cachetools
# NOC modules
from dialplan import DialPlan
from noc.lib.nosql import PlainReferenceField

id_lock = Lock()


class NumberCategoryRule(EmbeddedDocument):
    dialplan = PlainReferenceField(DialPlan)
    mask = StringField()
    is_active = BooleanField()
    description = StringField()


class NumberCategory(Document):
    meta = {
        "collection": "noc.numbercategories"
    }

    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    order = IntField(default=1000)
    rules = ListField(EmbeddedDocumentField(NumberCategoryRule))

    _id_cache = cachetools.TTLCache(100, ttl=60)
    _rule_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return NumberCategory.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"),
                             lock=lambda _: id_lock)
    def get_rules(cls):
        r = []
        for nc in NumberCategory.objects.filter(is_active=True).order_by("order"):
            for rule in nc.rules:
                if not rule.is_active:
                    continue
                r += [(
                    rule.dialplan,
                    re.compile(rule.mask),
                    nc
                )]
        return r
