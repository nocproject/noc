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
        "collection": "noc.sa.objectcapabilities"
    }
    object = ForeignKeyField(ManagedObject)
    caps = ListField(EmbeddedDocumentField(CapsItem))

    def __unicode__(self):
        return "%s caps" % self.object.name
