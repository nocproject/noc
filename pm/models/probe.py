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
from mongoengine.fields import (StringField, IntField, BooleanField,
                                ReferenceField)
## NOC Modules
from noc.main.models import User
from noc.lib.nosql import ForeignKeyField
from storage import Storage


class Probe(Document):
    """
    PM Probe daemon
    """
    meta = {
        "collection": "noc.pm.probe"
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    storage = ReferenceField(Storage)
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
