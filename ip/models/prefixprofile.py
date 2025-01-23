# ----------------------------------------------------------------------
# Prefix Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from functools import partial
from typing import Optional, Union, List
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    BooleanField,
    DateTimeField,
    EmbeddedDocumentListField,
    ReferenceField,
)
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.template import Template
from noc.main.models.label import Label
from noc.inv.models.resourcepool import ResourcePool
from noc.wf.models.workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_save, on_delete_check
from noc.core.scheduler.job import Job
from .addressprofile import AddressProfile

id_lock = Lock()


class PoolItem(EmbeddedDocument):
    pool = ReferenceField(ResourcePool, required=True)
    description = StringField()
    ip_filter = StringField()

    def __str__(self):
        return f"{self.pool}: {self.ip_filter}"


@Label.model
@on_save
@bi_sync
@on_delete_check(
    check=[
        ("ip.Prefix", "profile"),
        ("sa.ManagedObjectProfile", "prefix_profile_interface"),
        ("sa.ManagedObjectProfile", "prefix_profile_neighbor"),
        ("sa.ManagedObjectProfile", "prefix_profile_confdb"),
        ("vc.VPNProfile", "default_prefix_profile"),
        ("peer.ASProfile", "prefix_profile_whois_route"),
    ]
)
class PrefixProfile(Document):
    meta = {"collection": "prefixprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    # Enable nested Address discovery
    # via ARP cache
    enable_ip_discovery = BooleanField(default=False)
    # Enable nested Addresses discovery
    # via active PING probes
    enable_ip_ping_discovery = BooleanField(default=False)
    # Timestamp of last ip discovery synced
    ip_ping_discovery_last_run = DateTimeField()
    # Enable nested prefix discovery
    enable_prefix_discovery = BooleanField(default=False)
    # Prefix workflow
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "ip.PrefixProfile")
    )
    style = ForeignKeyField(Style)
    pools: List["PoolItem"] = EmbeddedDocumentListField(PoolItem)
    # Template.subject to render Prefix.name
    name_template = ForeignKeyField(Template)
    default_address_profile: Optional["AddressProfile"] = ReferenceField(
        AddressProfile, required=False
    )
    # Discovery policies
    prefix_discovery_policy = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="D")
    address_discovery_policy = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="D")
    # Send seen event to parent
    seen_propagation_policy = StringField(
        choices=[("P", "Propagate"), ("E", "Enable"), ("D", "Disable")], default="P"
    )
    # Include/Exclude broadcast & network addresses from prefix
    prefix_special_address_policy = StringField(
        choices=[("I", "Include"), ("X", "Exclude")], default="X"
    )
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
    _default_cache = cachetools.TTLCache(maxsize=10, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["PrefixProfile"]:
        return PrefixProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["PrefixProfile"]:
        return PrefixProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_prefixprofile")

    def on_save(self):
        self.ensure_ip_discovery_job()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "PrefixProfile":
        pp = AddressProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not pp:
            wf = Workflow.get_default_workflow("ip.Prefix")
            if not wf:
                wf = Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first()
            pp = PrefixProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                description="Default prefix profile",
                workflow=wf,
            )
            pp.save()
        return pp

    def ensure_ip_discovery_job(self):
        from noc.services.discovery.jobs.ipping.address import JCLS_IPPING_PREFIX

        if self.enable_ip_ping_discovery:
            Job.submit(
                "scheduler",
                JCLS_IPPING_PREFIX,
                key=str(self.id),
                data={"profile_id": str(self.id)},
            )
        else:
            Job.remove(
                "scheduler",
                JCLS_IPPING_PREFIX,
                key=str(self.id),
            )
            # PrefixProfile.objects.filter(id=self.id).update(ip_ping_discovery_last_run=None)
