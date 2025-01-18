# ----------------------------------------------------------------------
# ResourcePool model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import threading
import random
import string
import logging
import datetime
from typing import Optional, List, Union, Callable, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, IntField
import cachetools

# NOC Modules
from noc.core.lock.distributed import DistributedLock
from noc.core.lock.base import get_locked_items
from noc.core.model.decorator import on_delete_check
from noc.core.perf import metrics
from noc.models import get_model

id_lock = threading.Lock()

DISTRIBUTEDLOCK = "resourcepool"
DISTRIBUTEDLOCK_TTL = 600
TYPE_RESOURCE_MAP = {"vlan": "vc.VLAN", "ip": "ip.Address"}
logger = logging.getLogger(__name__)


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

    @property
    def resource_model(self):
        return get_model(TYPE_RESOURCE_MAP[self.type])

    def get_resource_domains(self) -> List[Any]:
        """Getting Resource Domains"""
        if self.type == "vlan":
            model = get_model("vc.L2Domain")
        elif self.type == "ip":
            model = get_model("ip.Prefix")
        else:
            raise NotImplementedError("IP Allocation is not Implemented yet")
        return model.get_by_resource_pool(self)

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

    def get_allocator(self, limit=1, **hints) -> Callable:
        """Return ResourceAllocator method"""
        li = get_locked_items()
        if self.get_lock_name() not in li:
            raise RuntimeError("Trying to allocate from non-locked pool")
        if self.type not in TYPE_RESOURCE_MAP:
            raise NotImplementedError(f"Allocator for type {self.type} is NotImplemented")
        model = self.resource_model
        if not hasattr(model, "get_resource_keys"):
            raise NotImplementedError(f"Allocator interface on model {model} NotImplementer")
        return self.allocate

    @classmethod
    def get_metrics(cls, pools: List["ResourcePool"]):
        """
        Getting metrics for pools: total, used (by count)
        1. Group by type
        2. Get metrics by resource
        3. Return metrics
        """

    def check_threshold(self, used: int, total: int) -> bool:
        """Check Pool Threshold"""

        used = round(total / used * 100, 2)
        if used > self.warn_threshold:
            # @todo send query
            return False
        return True

    def allocate(
        self,
        limit: int = 1,
        allocated_till: Optional[datetime.datetime] = None,
        allow_free: bool = False,
        reservation_id: Optional[str] = None,
        user: Optional[str] = None,
        confirm: bool = True,
        is_dirty: bool = False,
        # Hints
        resource_keys: Optional[List[str]] = None,
        domain: Optional[Any] = None,
        **kwargs,
    ):
        """
        Reserved free vlan for future used and create new
        Args:
            limit: Number of allocated
            allocated_till: Allocated till timestamp
            allow_free: Allow used free records
            reservation_id: External reservation id
            user: Allocated user
            confirm: Send Approve signal after reserve
            is_dirty: Not save created records and not send signal
            resource_keys: Preferred keys
            domain: Resource Domain

            kwargs: Allocator Hints
        """
        if domain:
            domains = [domain]
            # check domain in pool ?
        else:
            domains = self.get_resource_domains()
        if not domains:
            return
        allocated: List[Any] = []
        d = domains.pop()
        # Replace to hints
        pool_settings = d.get_pool_settings(self)
        processed = set()
        limit = len(resource_keys or []) or limit
        # ToDo Pool.threshold limit (max allocation by user)
        logger.info("[%s] Allocated records: %s", self.name, limit)
        # Processed free
        while len(allocated) < limit:
            # Requested resource keys
            logger.debug("[%s|%s] First allocated iteration", self.name, d.name)
            requested_limit = limit - len(allocated)
            keys = self.resource_model.get_resource_keys(
                d,
                vlan_filter=pool_settings.vlan_filter if pool_settings else None,
                limit=requested_limit,
                strategy=self.strategy,
                keys=resource_keys,
                exclude_keys=processed,
            )
            if not keys and not domains:
                logger.debug("[%s|%s] Nothing keys for allocated. Stop", self.name, d.name)
                break
            elif not keys:
                # additional domains if bad allocated
                logger.info(
                    "[%s|%s] Need more keys for allocated. Trying next: %s",
                    self.name,
                    d.name,
                    domains[0],
                )
                d = domains.pop()
                processed = set()
                continue
            if len(keys) > requested_limit:
                keys = keys[:requested_limit]
            # Set allocated state
            logger.debug("[%s|%s] Set allocated keys: %s", self.name, d.name, keys)
            for key, res, error in self.resource_model.iter_resources_by_key(
                keys,
                domain=d,
                allow_create=not is_dirty,
            ):
                if error:
                    logger.warning("[%s] Error when allocating resource: %s", res, error)
                    continue
                processed.add(key)
                if not is_dirty:
                    res.reserve(
                        allocated_till,
                        reservation_id=reservation_id,
                        confirm=confirm,
                        user=user,
                    )
                allocated.append(res)
        metrics["allocated_count", ("resource_pool", self.name)] += len(allocated)
        # errors_count
        # Errors
        return allocated
