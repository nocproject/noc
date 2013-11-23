## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelMapping model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField)
from noc.inv.models.objectmodel import ObjectModel
from noc.lib.nosql import PlainReferenceField


class ModelMapping(Document):
    meta = {
        "collection": "noc.modelmappings",
        "allow_inheritance": False
    }

    # Vendor, as returned by get_inventory
    vendor = StringField()
    # Part number, as returned by get_inventory
    part_no = StringField()
    # Serial number ranges, if applicable
    from_serial = StringField()
    to_serial = StringField()
    #
    model = PlainReferenceField(ObjectModel)
    #
    is_active = BooleanField(default=True)
    description = StringField(required=False)