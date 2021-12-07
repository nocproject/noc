# ----------------------------------------------------------------------
# L2Domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import itertools
import operator
from typing import Optional, List, Iterable

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    EmbeddedDocumentListField,
    ReferenceField,
)
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.wf.models.state import State
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check, on_save
from noc.inv.models.resourcepool import ResourcePool
from .vlanfilter import VLANFilter
from .vlantemplate import VLANTemplate
from .l2domainprofile import L2DomainProfile

id_lock = Lock()

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
@on_delete_check(check=[("vc.VLAN", "l2domain"), ("sa.ManagedObject", "l2_domain")])
class L2Domain(Document):
    meta = {
        "collection": "l2domains",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"unique": True, "fields": ["name", "pools.pool"]},
            "labels",
            "effective_labels",
        ],
    }

    name = StringField(unique=True)
    profile = PlainReferenceField(L2DomainProfile, default=L2DomainProfile.get_default_profile)
    description = StringField()
    # L2Domain workflow
    state = PlainReferenceField(State)
    pools = EmbeddedDocumentListField(PoolItem)
    #
    vlan_template = ReferenceField(VLANTemplate)
    # discovery_vlan_profile
    # local_filter
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

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["L2Domain"]:
        return L2Domain.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["L2Domain"]:
        return L2Domain.objects.filter(bi_id=id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_l2domain")

    def clean(self):
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
        vlan_template = self.get_effective_vlan_template()
        if vlan_template and vlan_template.type != "l2domain":
            raise ValidationError("Only l2domain VLAN Template type may be assign")

    def on_save(self):
        # Allocate vlans when necessary
        template = self.get_effective_vlan_template()
        if template:
            template.allocate_template(self.id)

    def get_effective_pools(self, pool: "ResourcePool" = None) -> List["PoolItem"]:
        """

        :param pool:
        :return:
        """
        return list(
            itertools.filterfalse(
                lambda x: pool and pool == x.pool,
                itertools.chain(self.profile.pools or [], self.pools or []),
            )
        )

    def get_effective_vlan_num(
        self,
        vlan_filter: Optional["VLANFilter"] = None,
        pool: "ResourcePool" = None,
        policy_order: bool = False,
    ) -> List[int]:
        """
        Build effective vlan number. Default - 1 - 4096 range
         If Set Pool - limit it by vlan_filter
        :param vlan_filter:
        :param pool: ResourcePool
        :param policy_order:  Return vlans in order by policy settings
        :return:
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

    def get_effective_vlan_template(self, type: Optional[str] = None) -> Optional["VLANTemplate"]:
        """
        Return Effective VLAN Template
        :param type:
        :return:
        """
        if self.vlan_template:
            return self.vlan_template
        return self.profile.vlan_template

    def get_used_vlan_labels(self) -> List[int]:
        """
        Return Used VLAN numbers - Not set by FREE_VLAN_STATE

        :return:
        """
        from noc.wf.models.state import State
        from .vlan import VLAN

        used_states = list(State.objects.filter(name__ne=FREE_VLAN_STATE).values_list("id"))
        return list(
            VLAN.objects.filter(l2domain=self.id, state__in=used_states).values_list("vlan")
        )

    def iter_free_vlan_labels(
        self,
        vlan_filter: Optional["VLANFilter"] = None,
        pool: "ResourcePool" = None,
    ) -> Iterable[int]:
        """
        Iterator over free VLAN numbers
        :param vlan_filter:
        :param pool:
        :return:
        """
        used_vlans = set(self.get_used_vlan_labels())
        # @todo convert used vlans to vlan_filter
        for r in self.get_effective_vlan_num(vlan_filter, pool, policy_order=True):
            if r in used_vlans:
                continue
            yield r

    def get_free_vlan_num(
        self,
        vlan_filter: Optional["VLANFilter"] = None,
        pool: "ResourcePool" = None,
    ) -> Optional[int]:
        """
        Find free label in L2 Domain
        :param vlan_filter: Optional VC Filter to restrict labels
        :param pool:
        :returns: Free label or None
        :rtype: int or None
        """

        return next(self.iter_free_vlan_labels(vlan_filter, pool), None)
