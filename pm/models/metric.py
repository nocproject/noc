## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-marty modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BinaryField, BooleanField


class Metric(Document):
    meta = {
        "collection": "noc.ts.metrics",
        "indexes": ["parent", ("parent", "local")]
    }

    name = StringField(unique=True)
    hash = BinaryField(unique=True)
    parent = BinaryField()
    # Name within parent
    local = StringField()
    has_children = BooleanField()

    def __unicode__(self):
        return self.name
