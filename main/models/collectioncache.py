## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CollectionCache model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, StringField, UUIDField)


class CollectionCache(Document):
    meta = {
        "collection": "noc.collectioncache",
        "allow_inheritance": False,
        "indexes": ["collection"]
    }

    collection = StringField()
    uuid = UUIDField(unique=True, binary=True)

    def unicode(self):
        return "%s:%s" % (self.collection, self.uuid)

    @classmethod
    def merge(cls, collection, uuids):
        """
        Merge UUIDs to cache
        """
        current = set(o.uuid for o in CollectionCache.objects.filter(
            collection=collection))
        for u in uuids - current:
            CollectionCache(collection=collection, uuid=u).save()
