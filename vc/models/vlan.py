# ----------------------------------------------------------------------
# VLAN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging
from typing import Optional, Iterator, Set, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    IntField,
    DateTimeField,
)
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from .vlanprofile import VLANProfile
from .l2domain import L2Domain
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_save, on_delete_check
from noc.core.perf import metrics
from noc.inv.models.resourcepool import ResourcePool
from noc.vc.models.vlanfilter import VLANFilter

id_lock = Lock()
logger = logging.getLogger(__name__)

FREE_VLAN_STATE = "Free"
FULL_VLAN_RANGE = set(range(1, 4096))


@Label.model
@bi_sync
@workflow
@on_save
@on_delete_check(check=[("ip.Prefix", "vlan")])
class VLAN(Document):
    meta = {
        "collection": "vlans",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["l2_domain", "vlan"], "unique": True},
            "expired",
            "labels",
            "effective_labels",
        ],
    }

    name = StringField(default="")
    profile = PlainReferenceField(
        VLANProfile, required=True, default=VLANProfile.get_default_profile
    )
    vlan = IntField(min_value=1, max_value=4095)
    l2_domain = PlainReferenceField(L2Domain, required=True)
    description = StringField()
    state = PlainReferenceField(State)
    project = ForeignKeyField(Project)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Discovery integration
    # Timestamp when object first discovered
    first_discovered = DateTimeField()
    # Timestamp when object last seen by discovery
    last_seen = DateTimeField()
    # Timestamp when send "expired" event
    expired = DateTimeField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return f"{self.l2_domain}:{self.vlan} ({self.name})"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VLAN"]:
        return VLAN.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["VLAN"]:
        return VLAN.objects.filter(bi_id=bi_id).first()

    @classmethod
    def get_component(cls, managed_object, vlan=None, **kwargs) -> Optional["VLAN"]:
        if not vlan:
            return
        if managed_object.l2_domain:
            return VLAN.objects.filter(l2_domain=managed_object.l2_domain, vlan=int(vlan)).first()

    def clean(self):
        super().clean()
        if not hasattr(self, "_changed_fields") or "l2_domain" in self._changed_fields:
            if self.vlan not in set(self.l2_domain.get_effective_vlan_id()):
                raise ValidationError(f"VLAN {self.vlan} not in allowed {self.l2_domain} range")

    @classmethod
    def iter_free(
        cls,
        l2_domain: "L2Domain",
        pool: "ResourcePool" = None,
        vlan_filter: "VLANFilter" = None,
        limit: int = 1,
        **kwargs,
    ) -> Iterator["VLAN"]:
        """
        Iter Free VLANs
        1. Check Exists VLANs with Free State
        2. Create VLAN on free state when needed

        :param pool: ResourcePool
        :param l2_domain:
        :param vlan_filter:
        :param limit: Resource Count
        :param kwargs: Additional hints for allocate
        :return:
        """
        from noc.wf.models.state import State

        if pool and not l2_domain.get_effective_pools(pool):
            # L2Domain not supported allocated vlan by pool
            return
        vlans: Set[int] = FULL_VLAN_RANGE
        if vlan_filter:
            vlans & set(vlan_filter.include_vlans)
        pools = l2_domain.get_effective_pools(pool)
        for pp in pools:
            vlans = vlans & set(pp.vlan_filter.include_vlans)
        # Check pool in VLAN
        free_states = list(State.objects.filter(name=FREE_VLAN_STATE).values_list("id"))
        free_vlans = VLAN.objects.filter(
            l2_domain=l2_domain, vlan__in=list(vlans), state__in=free_states
        ).limit(limit)
        if pool and pool.strategy == "L":
            free_vlans = free_vlans.order_by("-vlan")
        elif pool and pool.strategy == "F":
            free_vlans = free_vlans.order_by("vlan")
        allocated_count = 0
        # Iter Free VLANs
        for vlan in sorted(free_vlans, reverse=pool and pool.strategy == "L"):
            yield vlan
            allocated_count += 1
            vlans.remove(vlan.vlan)
        if allocated_count >= limit:
            return
        # @todo check Cooldown
        # @todo raise Overflow Resource if len(vlans) < limit - allocated_count
        # Iter vlan
        for vlan in vlans:
            if allocated_count >= limit:
                break
            vlan = cls.allocate(l2_domain, vlan)
            if not vlan:
                continue
            yield vlan
            allocated_count += 1

    @classmethod
    def allocate(
        cls, l2_domain: "L2Domain", vlan_id: int, name: Optional[str] = None
    ) -> Optional["VLAN"]:
        """
        Allocate vlan on L2Domain
        :param l2_domain:
        :param vlan_id:
        :param name:
        :return:
        """
        vlan = VLAN(
            vlan=vlan_id,
            l2_domain=l2_domain,
            profile=l2_domain.get_default_vlan_profile(),
            description="",
        )
        if name:
            vlan.name = name
        try:
            vlan.save()
            metrics["vlan_created"] += 1
        except Exception as e:
            logger.warning("[%s|%s] Error when create vlan: %s", l2_domain.name, vlan_id, str(e))
            return None
        return vlan

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vlan")
