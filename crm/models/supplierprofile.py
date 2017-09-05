# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Supplier Group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField
# NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.main.models.style import Style


class SupplierProfile(Document):
    meta = {
        "collection": "noc.supplierprofiles",
        "strict": False
    }

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    tags = ListField(StringField())

    def __unicode__(self):
        return self.name
