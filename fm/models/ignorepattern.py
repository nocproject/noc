# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IgnorePattern model
## Propagated to collectors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


class IgnorePattern(Document):
    meta = {
        "collection": "noc.fm.ignorepatterns",
        "allow_inheritance": False
    }

    source = StringField()
    pattern = StringField()
    is_active = BooleanField()
    description = StringField(required=False)

    def __unicode__(self):
        return u"%s: %s" % (self.source, self.pattern)
