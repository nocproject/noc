# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Enumeration model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import document, fields


class Enumeration(document.Document):
    meta = {
        "collection": "noc.enumerations",
        "allow_inheritance": False
    }

    name = fields.StringField(unique=True)
    is_builtin = fields.BooleanField(default=False)
    values = fields.DictField()  # value -> [possible combinations]

    def __unicode__(self):
        return self.name
