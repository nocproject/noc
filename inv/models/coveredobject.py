## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Covered Objects
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (IntField)
## NOC modules
from coverage import Coverage
from noc.inv.models.object import Object
from noc.lib.nosql import PlainReferenceField


class CoveredObject(Document):
    meta = {
        "collection": "noc.coveredobjects",
        "allow_inheritance": False,
        "indexes": ["coverage", "object"]
    }
    coverage = PlainReferenceField(Coverage)
    # Coverage preference.
    # The more is the better
    # Zero means coverage is explicitly disabled for ordering
    preference = IntField(default=100)

    object = PlainReferenceField(Object)

    def __unicode__(self):
        return u"%s %s" % (
            self.coverage.name,
            self.object.name or self.object.id
        )
