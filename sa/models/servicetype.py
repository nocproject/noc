# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Type
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField
## NOC modules


class ServiceType(Document):
    meta = {
        "collection": "noc.servicetypes",
        "json_collection": "sa.servicetypes"
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True, unique=True)
    description = StringField()
    # Optional data model identifier (i.e. sa.ManagedObject)
    model = StringField()

    def __unicode__(self):
        return self.name
