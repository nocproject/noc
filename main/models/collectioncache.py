<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CollectionCache model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CollectionCache model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import (Document, StringField, UUIDField)


class CollectionCache(Document):
    meta = {
        "collection": "noc.collectioncache",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
