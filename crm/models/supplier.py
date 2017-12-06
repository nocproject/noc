# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Supplier
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, BooleanField
# NOC modules
from .supplierprofile import SupplierProfile
from noc.lib.nosql import PlainReferenceField
from noc.wf.models.state import State


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

    def __unicode__(self):
        return self.name
