# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MaintainanceType
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


class MaintainanceType(Document):
    meta = {
        "collection": "noc.maintainancetype"
    }
    name = StringField(unique=True)
    description = StringField()
    suppress_alarms = BooleanField()
    card_template = StringField()

    def __unicode__(self):
        return self.name
