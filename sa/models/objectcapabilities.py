# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (ListField, StringField, ReferenceField,
                                DynamicField, EmbeddedDocumentField)
import mongoengine.signals
## NOC modules
from managedobject import ManagedObject
from noc.inv.models.capability import Capability
from noc.lib.nosql import ForeignKeyField


class CapsItem(EmbeddedDocument):
    capability = ReferenceField(Capability)
    discovered_value = DynamicField()
    local_value = DynamicField(default=None)

    def __unicode__(self):
        return self.capability.name


class ObjectCapabilities(Document):
    meta = {
        "collection": "noc.sa.objectcapabilities",
        "indexes": ["object"]
    }
    object = ForeignKeyField(ManagedObject)
    caps = ListField(EmbeddedDocumentField(CapsItem))

    def __unicode__(self):
        return "%s caps" % self.object.name

    @classmethod
    def on_change_object_caps(cls, sender, document=None, *args, **kwargs):
        from noc.inv.discovery.scheduler import get_scheduler
        get_scheduler().on_change_object_caps(document.object)

##
from noc.pm.models.probeconfig import ProbeConfig
mongoengine.signals.post_save.connect(
    ProbeConfig.on_change_object_caps,
    sender=ObjectCapabilities
)
mongoengine.signals.post_save.connect(
    ObjectCapabilities.on_change_object_caps,
    sender=ObjectCapabilities
)
