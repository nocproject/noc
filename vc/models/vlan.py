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
from typing import Optional, Iterable, List, Set

# Third-party modules
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
from noc.core.model.decorator import on_save
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
class VLAN(Document):
    meta = {
        "collection": "vlans",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["l2domain", "vlan"], "unique": True},
            "expired",
            "labels",
            "effective_labels",
        ],
    }

    name = StringField()
    profile = PlainReferenceField(VLANProfile)
    vlan = IntField(min_value=1, max_value=4095)
    l2domain = PlainReferenceField(L2Domain)
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
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["VLAN"]:
        return VLAN.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["VLAN"]:
        return VLAN.objects.filter(bi_id=id).first()

    def clean(self):
        super().clean()
        if not hasattr(self, "_changed_fields") or "l2domain" in self._changed_fields:
            if self.vlan not in set(self.l2domain.get_effective_vlan_num()):
                raise ValidationError(f"VLAN {self.vlan} not in allowed {self.l2domain} range")

    @classmethod
    def iter_free(
        cls,
        l2_domain: "L2Domain",
        pool: "ResourcePool" = None,
        vlan_filter: "VLANFilter" = None,
        limit: int = 1,
        **kwargs,
    ) -> Iterable["VLAN"]:
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

        if pool and not l2_domain.pools:
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
            l2domain=l2_domain, vlan__in=list(vlans), state__in=free_states
        ).limit(limit)
        if pool and pool.strategy == "L":
            free_vlans = free_vlans.sorted({"vlan": 1})
        elif pool and pool.strategy == "F":
            free_vlans = free_vlans.sorted({"vlan": -1})
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
    def allocate(cls, l2_domain: "L2Domain", vlan_num: int) -> Optional["VLAN"]:
        """
        Allocate vlan on L2Domain
        :param l2_domain:
        :param vlan_num:
        :return:
        """
        vlan = VLAN(
            vlan=vlan_num, l2_domain=l2_domain, profile=l2_domain.get_vlan_profile(), description=""
        )
        try:
            vlan.save()
        except Exception:
            return None
        return vlan

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vlan")
