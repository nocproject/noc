## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMProbe model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import Document, StringField, BooleanField


class PMProbe(Document):
    """
    PM Probe daemon
    """
    meta = {
        "collection": "noc.pm.probe",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.name
