# ----------------------------------------------------------------------
# L2Domain Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import itertools
import operator

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
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.inv.models.resourcepool import ResourcePool
from .vlanfilter import VLANFilter
from .vlantemplate import VLANTemplate
from .vlanprofile import VLANProfile

id_lock = Lock()


class PoolItem(EmbeddedDocument):
    pool = ReferenceField(ResourcePool, required=True)
    description = StringField()
    vlan_filter = ReferenceField(VLANFilter)

    def __str__(self):
        return f"{self.pool}: {self.vlan_filter}"


@Label.model
@bi_sync
@on_delete_check(check=[("vc.L2Domain", "profile")])
class L2DomainProfile(Document):
    meta = {
        "collection": "l2domainprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["labels"],
    }

    name = StringField(unique=True)
    description = StringField()
    # L2Domain workflow
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style)
    pools = EmbeddedDocumentListField(PoolItem)
    #
    vlan_template = ReferenceField(VLANTemplate)
    default_vlan_profile = ReferenceField(VLANProfile, required=False)
    # Discovery settings
    vlan_discovery_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("E", "Enable"),
            ("S", "Status Only"),
        ],
        default="E",
    )
    vlan_discovery_filter = ReferenceField(VLANFilter)  # local_filter
    # local_filter
    # Labels
    labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["L2DomainProfile"]:
        return L2DomainProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["L2DomainProfile"]:
        return L2DomainProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_l2domain")

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "L2DomainProfile":
        l2p = L2DomainProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not l2p:
            l2p = L2DomainProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            l2p.save()
        return l2p

    def clean(self):
        if self.vlan_template and self.vlan_template.type != "l2domain":
            raise ValidationError("Only l2domain VLAN Template type may be assign")
        pools = [v.pool.id for v in self.pools]
        if len(pools) != len(set(pools)):
            raise ValidationError("Resource Pools must by unique")
        vlan_filters = list(
            itertools.chain.from_iterable(
                [v.vlan_filter.include_vlans for v in self.pools if v.vlan_filter]
            )
        )
        if vlan_filters and len(vlan_filters) != len(set(vlan_filters)):
            raise ValidationError("VLAN Filter overlapped")
