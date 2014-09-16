## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMProbe model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import mongoengine.signals
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField)
## NOC Modules
from noc.main.models import User
from noc.lib.nosql import ForeignKeyField


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
    n_instances = IntField(default=1)

    def __unicode__(self):
        return self.name

##
from probeconfig import ProbeConfig
mongoengine.signals.post_save.connect(
    ProbeConfig.on_change_probe,
    sender=Probe
)
