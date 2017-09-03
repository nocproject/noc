# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField,
                                ListField)
# NOC modules
from slaprofile import SLAProfile
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


PROBE_TYPES = IGetSLAProbes.returns.element.attrs["type"].choices


class SLAProbe(Document):
    meta = {
        "collection": "noc.sla_probes",
        "strict": False,
        "indexes": [
            "managed_object"
        ]
    }

    managed_object = ForeignKeyField(ManagedObject)
    # Probe name (<managed object>, <group>, <name> triple must be unique
    name = StringField()
    # Probe profile
    profile = PlainReferenceField(SLAProfile)
    # Probe group
    group = StringField()
    # Optional description
    description = StringField()
    # Probe type
    type = StringField(choices=[(x, x) for x in PROBE_TYPES])
    # IP address or URL, depending on type
    target = StringField()
    # Hardware timestamps
    hw_timestamp = BooleanField(default=False)
    # Optional tags
    tags = ListField(StringField())

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)
