# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmPlugin model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import fields
from mongoengine.document import EmbeddedDocument, Document


class AlarmPlugin(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }

    name = fields.StringField()
    config = fields.DictField(default={})

    def __unicode__(self):
        return self.name
