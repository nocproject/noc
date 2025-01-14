# ----------------------------------------------------------------------
# L2Domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import operator
import logging
from threading import Lock
from typing import Optional, Union, Iterable, List, Dict

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    EmbeddedDocumentListField,
    ReferenceField,
)
from mongoengine.errors import ValidationError
from mongoengine.queryset.visitor import Q
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.wf.models.state import State
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check, on_save
from noc.inv.models.resourcepool import ResourcePool
from .vlanprofile import VLANProfile
from .vlanfilter import VLANFilter
from .vlantemplate import VLANTemplate
from .l2domainprofile import L2DomainProfile

id_lock = Lock()
logger = logging.getLogger(__name__)

FREE_VLAN_STATE = "Free"
FULL_VLAN_RANGE = set(range(1, 4096))


class PoolItem(EmbeddedDocument):
    pool = ReferenceField(ResourcePool, required=True)
    description = StringField()
    vlan_filter = ReferenceField(VLANFilter)

    def __str__(self):
        return f"{self.pool}: {self.vlan_filter}"


@Label.model
@bi_sync
@on_save
@on_delete_check(
    check=[("vc.VLAN", "l2_domain"), ("sa.ManagedObject", "l2_domain")],
    clean=[("inv.SubInterface", "l2_domain")],
)
class L2Domain(Document):
    meta = {
        "collection": "l2domains",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "labels",
            "effective_labels",
        ],
    }

    name = StringField(unique=True)
    profile: "L2DomainProfile" = PlainReferenceField(
        L2DomainProfile, default=L2DomainProfile.get_default_profile
    )
    description = StringField()
    # L2Domain workflow
    state = PlainReferenceField(State)
    pools: List[PoolItem] = EmbeddedDocumentListField(PoolItem)
    #
    vlan_template = ReferenceField(VLANTemplate)
    default_vlan_profile: "VLANProfile" = ReferenceField(VLANProfile, required=False)
    # Discovery settings
    vlan_discovery_policy = StringField(
        choices=[
            ("P", "Profile"),
            ("F", "Disable"),
            ("E", "Enable"),
            ("S", "Status Only"),
        ],
        default="P",
    )
    vlan_discovery_filter = ReferenceField(VLANFilter)  # local_filter
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _l2_domains_mo_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["L2Domain"]:
        return L2Domain.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["L2Domain"]:
        return L2Domain.objects.filter(bi_id=bi_id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_l2domain")

    @classmethod
    def get_by_resource_pool(cls, pool: ResourcePool) -> List["L2Domain"]:
        """Getting L2Domains for resource pool"""
        q = Q(pools__pool=pool)
        profiles = list(L2DomainProfile.objects.filter(pools__pool=pool))
        if profiles:
            q |= Q(profile__in=profiles)
        return list(L2Domain.objects.filter(q))

    def iter_pool_settings(self) -> Iterable[PoolItem]:
        """Iterate over pool item"""
        processed = []
        for p in self.pools:
            processed.append(p.pool.id)
            yield p
        for p in self.profile.pools:
            if p.pool.id in processed:
                continue
            yield p

    def get_pool_settings(self, pool) -> Optional[PoolItem]:
        """Getting pool setting for L2Domain"""
        for p in self.iter_pool_settings():
            if p.pool == pool:
                return p

    def clean(self):
        pools = [pp.pool.id for pp in self.get_effective_pools()]
        if len(pools) != len(set(pools)):
            raise ValidationError("Resource Pool must by unique")
        # Check VLAN Filter Overlaps
        vlan_filters = list(
            itertools.chain.from_iterable(
                [
                    pp.vlan_filter.include_vlans
                    for pp in self.get_effective_pools()
                    if pp.vlan_filter
                ]
            )
        )
        if len(vlan_filters) != len(set(vlan_filters)):
            raise ValidationError("VLAN Filter overlapped")
        # Check Unique Pools overlap
        # Check VLAN Template type
        vlan_template = self.get_effective_vlan_template()
        if vlan_template and vlan_template.type != "l2domain":
            raise ValidationError("Only l2domain VLAN Template type may be assign")

    def on_save(self):
        from noc.sa.models.managedobject import ManagedObject

        # Allocate vlans when necessary
        template = self.get_effective_vlan_template()
        if template:
            template.allocate_template(self.id)
        if hasattr(self, "_changed_fields") and "profile" in self._changed_fields:
            for mo_id in self.get_l2_domain_object_ids(str(self.id)):
                ManagedObject._reset_caches(mo_id)

    def get_effective_pools(self, pool: "ResourcePool" = None) -> List["PoolItem"]:
        """"""
        return list(
            itertools.filterfalse(
                lambda x: pool and pool.id != x.pool.id,
                itertools.chain(self.profile.pools or [], self.pools or []),
            )
        )

    def get_default_vlan_profile(self) -> Optional["VLANProfile"]:
        """
        Return Effective VLAN Profile
        * L2Domain
        * L2DomainProfile
        * Default
        :return:
        """
        if self.default_vlan_profile:
            return self.default_vlan_profile
        if self.profile.default_vlan_profile:
            return self.profile.default_vlan_profile
        return VLANProfile.get_default_profile()

    def get_effective_vlan_template(self) -> Optional["VLANTemplate"]:
        """Return Effective VLAN Template"""
        if self.vlan_template:
            return self.vlan_template
        return self.profile.vlan_template

    def get_vlan_discovery_policy(self) -> str:
        if self.vlan_discovery_policy == "P":
            return self.profile.vlan_discovery_policy
        return self.vlan_discovery_policy

    def get_vlan_discovery_filter(self) -> Optional["VLANFilter"]:
        if self.vlan_discovery_filter:
            return self.vlan_discovery_filter
        return self.profile.vlan_discovery_filter

    def get_effective_vlan_id(
        self,
        vlan_filter: Optional["VLANFilter"] = None,
        pool: "ResourcePool" = None,
        policy_order: bool = False,
    ) -> List[int]:
        """
        Build effective vlan number. Default - 1 - 4096 range
         If Set Pool - limit it by vlan_filter
         Args:
            vlan_filter:
            pool: ResourcePool
            policy_order:  Return Vlans in order by policy settings
        """
        # Full VLAN range
        vlans = FULL_VLAN_RANGE
        if vlan_filter:
            vlans = vlans & set(vlan_filter.include_vlans)
        r = []
        for pp in self.get_effective_pools(pool):
            vlans = vlans & set(pp.vlan_filter.include_vlans)
            if policy_order:
                r += pp.pool.apply_resource_policy(list(vlans))
        if not policy_order:
            r = list(vlans)
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_l2_domains_mo_cache"), lock=lambda _: id_lock)
    def get_l2_domain_object_ids(cls, l2_domain: str):
        """Get list of all managed object ids belonging to same L2 domain"""
        from noc.sa.models.managedobject import ManagedObject

        return list(ManagedObject.objects.filter(l2_domain=l2_domain).values_list("id", flat=True))

    @classmethod
    def calculate_stats(cls, l2_domains: List["L2Domain"]) -> List[Dict[str, Union[str, int]]]:
        """Calculate statistics Pool usage"""
        # l2
        return []
