# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (ListField, StringField, ReferenceField,
                                DynamicField, EmbeddedDocumentField)
## NOC modules
from noc.inv.models.capability import Capability
from managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save
from noc.core.cache.base import cache


class CapsItem(EmbeddedDocument):
    capability = ReferenceField(Capability)
    discovered_value = DynamicField()
    local_value = DynamicField(default=None)

    def __unicode__(self):
        return self.capability.name


@on_save
class ObjectCapabilities(Document):
    meta = {
        "collection": "noc.sa.objectcapabilities",
        "indexes": ["object"]
    }
    object = ForeignKeyField(ManagedObject)
    caps = ListField(EmbeddedDocumentField(CapsItem))

    def __unicode__(self):
        return "%s caps" % self.object.name

    def on_save(self):
        cache.delete("cred-%s" % self.object.id)

    @classmethod
    def get_capabilities(cls, object):
        """
        Returns a dict of object's
        """
        if hasattr(object, "id"):
            object = object.id
        caps = {}
        oc = ObjectCapabilities._get_collection().find_one({
            "object": object
        }, {
            "_id": 0,
            "caps": 1
        })
        if oc:
            for c in oc["caps"]:
                lv = c.get("local_value")
                v = lv if lv else c.get("discovered_value")
                if v is not None:
                    # Resolve capability name
                    cc = Capability.get_by_id(c["capability"])
                    if cc:
                        caps[cc.name] = v
        return caps
