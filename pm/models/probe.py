## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMProbe model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, StringField,
                           BooleanField, ForeignKeyField)
from noc.main.models import User


class Probe(Document):
    """
    PM Probe daemon
    """
    meta = {
        "collection": "noc.pm.probe",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    user = ForeignKeyField(User)

    def __unicode__(self):
        return self.name
