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
from typing import Optional, List
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


class PoolItem(EmbeddedDocument):
    pool = ReferenceField(ResourcePool, required=True)
    description = StringField()
    vlan_filter = ReferenceField(VLANFilter)

    def __str__(self):
        return f"{self.pool}: {self.vlan_filter}"


@Label.model
@bi_sync
@on_save
@on_delete_check(check=[("vc.VLAM", "l2domain")])
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
    def get_by_id(cls, id) -> Optional["L2DomainProfile"]:
        return L2DomainProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["L2DomainProfile"]:
        return L2DomainProfile.objects.filter(bi_id=id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_l2domain")

    def clean(self):
        vlan_filters = list(
            itertools.chain.from_iterable(
                [v.vlan_filter.include_expression for v in self.pools if v.vlan_filter]
            )
        )
        if len(vlan_filters) != len(set(vlan_filters)):
            raise ValidationError("VLAN Filter overlapped")

    def on_save(self):
        # Allocate vlans when necessary
        template = self.get_effective_vlan_template()
        if template:
            template.allocate_template(self.id)

    def get_effective_pools(
        self, vlan_filter: Optional["VLANFilter"] = None
    ) -> List["PoolItem"]:
        r = []
        if self.profile.pools:
            r += self.profile.pools
        r += self.pools or []
        return r

    def get_effective_vlan_num(self, vlan_filter: Optional["VLANFilter"] = None) -> List[int]:
        """
        Build effective vlan number. Default - 1 - 4096 range
         If Set Pool - limit it by vlan_filter
        :param vlan_filter:
        :return:
        """
        # Full VLAN range
        vlans = set(range(1, 4096))
        # Build VLAN Filter
        v_filter = set(vlan_filter.include_vlans if vlan_filter else [])
        v_filter |= set(
            itertools.chain.from_iterable(
                [v.vlan_filter.include_vlans for v in self.get_effective_pools() if v.vlan_filter]
            )
        )
        # Build Exclude Filter
        ve_filter = set(vlan_filter.exclude_vlans if vlan_filter else [])
        ve_filter |= set(
            itertools.chain.from_iterable(
                [
                    v.vlan_filter.exclude_vlans or []
                    for v in self.get_effective_pools()
                    if v.vlan_filter and v.vlan_filter.exclude_expression
                ]
            )
        )
        # Return effective vlans
        return list(vlans.intersection(v_filter) - ve_filter)

    def get_effective_vlan_template(self, type: Optional[str] = None) -> Optional["VLANTemplate"]:
        """
        Return Effective VLAN Template
        :param type:
        :return:
        """
        if self.profile.vlan_template:
            return self.profile.vlan_template
        return self.vlan_template

    def get_free_vlan_num(
        self, vlan_filter: Optional["VLANFilter"] = None, pool: "ResourcePool" = None
    ) -> Optional[int]:
        """
        Find free label in L2 Domain
        :param vlan_filter: Optional VC Filter to restrict labels
        :param pool:
        :returns: Free label or None
        :rtype: int or None
        """
        from noc.wf.models.state import State
        from .vlan import VLAN

        states = list(State.objects.filter(is_productive=True).values_list("id"))
        active_vlans = set(VLAN.objects.filter(l2domain=self.id, state__in=states).values_list("vlan"))
        for pp in self.pools:
            r = set(pp.vlan_filter.include_vlans) - active_vlans
            if r:
                return pp.pool.get_resource(list(r))
        vlans = self.get_effective_vlan_num(vlan_filter)
        return vlans[0] if vlans else None
