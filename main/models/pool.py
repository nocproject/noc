# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Pool model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import operator
# Python modules
import threading
import time

import cachetools
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, LongField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = threading.Lock()


@bi_sync
@on_delete_check(check=[
    ("sa.ManagedObject", "pool"),
    # ("fm.EscalationItem", "administrative_domain")
])
class Pool(Document):
    meta = {
        "collection": "noc.pools",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True, min_length=1, max_length=16,
                       regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()
    discovery_reschedule_limit = IntField(default=50)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(1000, ttl=60)
    _name_cache = cachetools.TTLCache(1000, ttl=60)
    reschedule_lock = threading.Lock()
    reschedule_ts = {}  # pool id -> timestamp

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Pool.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return Pool.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return Pool.objects.filter(name=name).first()

    def get_delta(self):
        """
        Get delta for next discovery,
        Limit runs to discovery_reschedule_limit tasks
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
