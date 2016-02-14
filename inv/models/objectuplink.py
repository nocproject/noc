# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object uplink map
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ListField


class ObjectUplink(Document):
    meta = {
        "collection": "noc.objectuplinks",
        "indexes": ["uplinks"]
    }
    object = IntField(primary_key=True)
    uplinks = ListField(IntField())

    @classmethod
    def update_uplinks(cls, umap):
        if not umap:
            return
        bulk = ObjectUplink._get_collection().initialize_unordered_bulk_op()
        for o, uplinks in umap.iteritems():
            bulk.find({"_id": o}).upsert().update({
                "$set": {
                    "uplinks": uplinks
                }
            })
        bulk.execute()
