# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TTSystem
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField


class TTSystem(Document):
    meta = {
        "collection": "noc.ttsystem",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    handler = StringField()
    description = StringField()
    # Connection string
    connection = StringField()

    def __unicode__(self):
        return self.name
