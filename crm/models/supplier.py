# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Supplier
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, BooleanField
import cachetools
# NOC modules
from .supplierprofile import SupplierProfile
from noc.lib.nosql import PlainReferenceField
from noc.wf.models.state import State

id_lock = Lock()


class Supplier(Document):
    meta = {
        "collection": "noc.suppliers",
        "indexes": [
            "name"
        ],
        "strict": False,
        "auto_create_index": False
    }

    name = StringField()
    description = StringField()
    is_affilated = BooleanField(default=False)
    profile = PlainReferenceField(SupplierProfile)
    state = PlainReferenceField(State)
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Supplier.objects.filter(id=id).first()
