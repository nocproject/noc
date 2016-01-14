# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supplier
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ReferenceField, ListField,
                                BooleanField)
## NOC modules
from supplierprofile import SupplierProfile


class Supplier(Document):
    meta = {
        "collection": "noc.suppliers"
    }

    name = StringField()
    description = StringField()
    is_affilated = BooleanField(default=False)
    profile = ReferenceField(SupplierProfile)
    tags = ListField(StringField())

    def __unicode__(self):
        return self.name
