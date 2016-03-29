# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TTSystem
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField
from noc.lib.solutions import get_solution


class TTSystem(Document):
    meta = {
        "collection": "noc.ttsystem",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    # Full path to BaseTTSystem instance
    handler = StringField()
    description = StringField()
    # Connection string
    connection = StringField()
    #
    tags = ListField(StringField())

    def __unicode__(self):
        return self.name

    def get_system(self):
        """
        Return BaseTTSystem instance
        """
        h = get_solution(self.handler)
        if not h:
            raise ValueError
        return h(self.name, self.connection)
