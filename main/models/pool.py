# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pool model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import time
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
import cachetools

id_lock = threading.Lock()


class Pool(Document):
    meta = {
        "collection": "noc.pools"
    }

    name = StringField(unique=True, min_length=1, max_length=16,
                       regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return Pool.objects.get(id=id)
        except Pool.DoesNotExists:
            return None
