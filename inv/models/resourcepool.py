# ----------------------------------------------------------------------
# ResourcePool model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import threading
import random
import string
from typing import Optional, List, Iterator, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, IntField
import cachetools

# NOC Modules
from noc.core.lock.distributed import DistributedLock
from noc.core.lock.base import get_locked_items
from noc.core.model.decorator import on_delete_check
from noc.models import get_model

id_lock = threading.Lock()

DISTRIBUTEDLOCK = "resourcepool"
DISTRIBUTEDLOCK_TTL = 600
TYPE_RESOURCE_MAP = {"vlan": "vc.VLAN"}


def get_api_code_default():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(20))


@on_delete_check(check=[("vc.L2Domain", "pools.pool"), ("vc.L2DomainProfile", "pools.pool")])
class ResourcePool(Document):
    """
    ResourcePool

    Abstraction to restrict Resources - IP, VLAN
    """

    meta = {
        "collection": "resourcepools",
        "strict": False,
        "auto_create_index": False,
        "indexes": [{"fields": ["type", "api_code"], "unique": True}],
    }

    # Poole name
    name = StringField(unique=True)
    description = StringField()
    # Resource type ?general
    type = StringField(
        choices=[
            ("ip", "IP"),
            ("vlan", "Vlan"),
        ],
        required=True,
    )
    # Only one resource copy in pool
    is_unique = BooleanField(default=False)
    # ?Number ResourceCopy ?
    # How resource allocate
    strategy = StringField(
        choices=[
            ("F", "First"),
            ("L", "Last"),
            ("R", "Random"),
        ],
        default="F",
    )
    api_code = StringField(required=True, default=get_api_code_default)
    # API Role
    api_role = StringField(default="nbi:allocate")
    # notification_group - ?Notification event
    # Filled warning Threshold
    warn_threshold = IntField(min_value=0, max_value=100, default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return f"{self.type}: {self.name}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ResourcePool"]:
        return ResourcePool.objects.filter(id=oid).first()

    @classmethod
    def acquire(cls, pools: List["ResourcePool"], owner: Optional[str] = None):
        """
        # Set Lock
        with ResourcePool.acquire([pool1, ..., poolN]):
            for pool in pools:
                allocator = pool.get_allocator()
                for resource in allocator:
                    resource.
        return

        :param pools:
        :param owner:
        :return:
        """
        owner = owner or get_api_code_default()
        # generate owner - request_id, BuildFunction
        lock = DistributedLock(DISTRIBUTEDLOCK, owner, ttl=DISTRIBUTEDLOCK_TTL)
        return lock.acquire([p.get_lock_name() for p in pools])

    def get_lock_name(self):
        return f"rp:{self.id}"

    def get_allocator(self, limit=1, **hints) -> Iterator:
        """
        Return ResourceAllocator method
        :return:
        """
        li = get_locked_items()
        if self.get_lock_name() not in li:
            raise RuntimeError("Trying to allocate from non-locked pool")
        if self.type not in TYPE_RESOURCE_MAP:
            raise NotImplementedError(f"Allocator for type {self.type} is NotImplemented")
        model = get_model(TYPE_RESOURCE_MAP[self.type])
        if not hasattr(model, "iter_free"):
            raise NotImplementedError(f"Allocator interface on model {model} NotImplementer")
        try:
            allocator = getattr(model, "iter_free")
        except AttributeError as e:
            raise AttributeError(f"Required attribute {e}")
        return allocator(pool=self, limit=limit, **hints)

    @classmethod
    def get_metrics(cls, pools: List["ResourcePool"]):
        """
        Getting metrics for pools: total, used (by count)
        1. Group by type
        2. Get metrics by resource
        3. Return metrics
        :param pools:
        :return:
        """
        ...

    def check_threshold(self, used: int, total: int) -> bool:
        """
        Check Pool Threshold
        :return:
        """

        used = round(total / used * 100, 2)
        if used > self.warn_threshold:
            # @todo send query
            return False
        return True
