# ----------------------------------------------------------------------
# L2Domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
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
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.state import State
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
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
    template = ReferenceField(VLANTemplate)
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
