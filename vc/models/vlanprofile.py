# ----------------------------------------------------------------------
# VLAN Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField, EnumField
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.vlanroles import VLANRole

id_lock = Lock()


VLAN_ROLE_LABEL_SCOPE = "vlanrole"


@Label.model
@on_save
@bi_sync
@on_delete_check(
    check=[
        ("vc.VLAN", "profile"),
        ("vc.L2Domain", "default_vlan_profile"),
        ("vc.L2DomainProfile", "default_vlan_profile"),
        ("inv.NetworkSegmentProfile", "default_vlan_profile"),
    ]
)
class VLANProfile(Document):
    meta = {
        "collection": "vlanprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["labels"],
    }

    name = StringField(unique=True)
    description = StringField()
    # VLAN workflow
    workflow = PlainReferenceField(Workflow, required=True)
    style = ForeignKeyField(Style)
    role: Optional[VLANRole] = EnumField(VLANRole, required=False)
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
    _default_cache = cachetools.TTLCache(maxsize=10, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VLANProfile"]:
        return VLANProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["VLANProfile"]:
        return VLANProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vlan")

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "VLANProfile":
        vp = VLANProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not vp:
            vp = VLANProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                description="Default VLAN Profile",
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            vp.save()
        return vp

    @property
    def role_label(self):
        """Generate role label"""
        if not self.role:
            return None
        elif self.role == VLANRole.PROFILE:
            return f"{VLAN_ROLE_LABEL_SCOPE}::{self.name}"
        return f"{VLAN_ROLE_LABEL_SCOPE}::{self.role.value}"

    def on_save(self):
        if self.role_label:
            Label.ensure_label(self.role_label, model_ids=["vc.VLAN", "inv.Interface"])
