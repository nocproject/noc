# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pool model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField


class Pool(Document):
    meta = {
        "collection": "noc.pools"
    }

    name = StringField(unique=True, min_length=1, max_length=16,
                       regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()

    def __unicode__(self):
        return self.name
