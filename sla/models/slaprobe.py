# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField,
                                ListField, EmbeddedDocumentField)
# NOC modules
from slaprofile import SLAProfile
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


PROBE_TYPES = (IGetSLAProbes.returns
               .element.attrs["tests"]
               .element.attrs["type"].choices)


class SLAProbeTest(EmbeddedDocument):
    name = StringField()
    type = StringField(choices=[(x, x) for x in PROBE_TYPES])
    target = StringField()
    hw_timestamp = BooleanField(default=False)


class SLAProbe(Document):
    meta = {
        "collection": "noc.sla_probes",
        "strict": False,
        "indexes": [
            "managed_object"
        ]
    }

    managed_object = ForeignKeyField(ManagedObject)
    # Unique probe name (within M. O.)
    name = StringField()
    #
    profile = PlainReferenceField(SLAProfile)
    #
    description = StringField()
    #
    tests = ListField(EmbeddedDocumentField(SLAProbeTest))

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)
