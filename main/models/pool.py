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
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField


class Pool(Document):
    meta = {
        "collection": "noc.pools"
    }

    name = StringField(unique=True, min_length=1, max_length=16,
                       regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()
    discovery_reschedule_limit = IntField(default=50)

    _name_cache = {}

    reschedule_lock = threading.Lock()
    reschedule_ts = {}  # pool id -> timestamp

    def __unicode__(self):
        return self.name

    @classmethod
    def get_name_by_id(cls, id):
        id = str(id)
        if id not in cls._name_cache:
            try:
                cls._name_cache[id] = Pool.objects.get(id=id).name
            except Pool.DoesNotExist:
                cls._name_cache[id] = None
        return cls._name_cache[id]

    def get_delta(self):
        """
        Get delta for next discovery
        """
        t = time.time()
        dt = 1.0 / float(self.discovery_reschedule_limit)
        with self.reschedule_lock:
            lt = self.reschedule_ts.get(self.id)
            if lt and lt > t:
                delta = lt - t
            else:
                delta = 0
            self.reschedule_ts[self.id] = t + dt
        return delta
