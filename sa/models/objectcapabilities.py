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
    _capability_name = {}

    def __unicode__(self):
        return "%s caps" % self.object.name

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
                    cn = cls._capability_name.get(c["capability"])
                    if not cn:
                        cc = Capability._get_collection().find_one({
                            "_id": c["capability"]
                        }, {
                            "_id": 0,
                            "name": 1
                        })
                        if cc:
                            cn = cc["name"]
                        else:
                            cn = None
                        cls._capability_name[c["capability"]] = cn
                    # Store name
                    if cn:
                        caps[cn] = v
        return caps
