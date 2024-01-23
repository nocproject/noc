# ---------------------------------------------------------------------
# Pool model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import time
import operator
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, LongField
import cachetools

# NOC Modules
from noc.main.models.label import Label
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync

id_lock = threading.Lock()


@Label.match_labels("pool", allowed_op={"="})
@bi_sync
@change
@on_delete_check(
    check=[
        ("sa.AdministrativeDomain", "default_pool"),
        ("sa.DiscoveredObject", "pool"),
        ("sa.ObjectDiscoveryRule", "network_ranges__pool"),
        ("sa.ManagedObject", "pool"),
        ("sa.ManagedObject", "fm_pool"),
        ("inv.CPEProfile", "object_pool"),
        # ("fm.EscalationItem", "administrative_domain")
    ],
    clean_lazy_labels="pool",
)
class Pool(Document):
    meta = {"collection": "noc.pools", "strict": False, "auto_create_index": False}

    name = StringField(unique=True, min_length=1, max_length=16, regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()
    discovery_reschedule_limit = IntField(default=50)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(1000, ttl=60)
    _name_cache = cachetools.TTLCache(1000, ttl=60)
    reschedule_lock = threading.Lock()
    reschedule_ts = {}  # pool id -> timestamp

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Pool"]:
        return Pool.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Pool"]:
        return Pool.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["Pool"]:
        return Pool.objects.filter(name=name).first()

    def get_delta(self) -> float:
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

    @classmethod
    def iter_lazy_labels(cls, pool: "Pool"):
        yield f"noc::pool::{pool.name}::="
