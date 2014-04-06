# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Street object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DictField, BooleanField, DateTimeField)
from noc.lib.nosql import PlainReferenceField
## NOC modules
from division import Division


class Street(Document):
    meta = {
        "collection": "noc.streets",
        "allow_inheritance": False,
        "indexes": ["parent", "data"]
    }
    #
    parent = PlainReferenceField(Division)
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Additional data
    # Depends on importer
    data = DictField()
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    def __unicode__(self):
        return "%s, %s" % (self.name, self.short_name)