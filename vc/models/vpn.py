# ----------------------------------------------------------------------
# VPN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, LongField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from .vpnprofile import VPNProfile
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


class RouteTargetItem(EmbeddedDocument):
    """
    Global (managed_object is None) or object-local VRF topology settings
    """

    rd = StringField()
    managed_object = ForeignKeyField(ManagedObject)
    # forwarding_instance
    op = StringField(choices=[("both", "both"), ("import", "import"), ("export", "export")])
    target = StringField()


@Label.model
@bi_sync
@on_delete_check(check=[("vc.VPN", "parent")])
@workflow
class VPN(Document):
    meta = {
        "collection": "vpns",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["labels", "effective_labels"],
    }

    name = StringField(unique=True)
    profile = PlainReferenceField(VPNProfile)
    description = StringField()
    state = PlainReferenceField(State)
    # Link to parent overlay
    parent = PlainReferenceField("self")
    project = ForeignKeyField(Project)
    route_target = ListField(EmbeddedDocumentField(RouteTargetItem))
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
    # @todo: last_seen
    # @todo: expired

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VPN"]:
        return VPN.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["VPN"]:
        return VPN.objects.filter(bi_id=bi_id).first()

    def clean(self):
        super().clean()
        if self.id and "parent" in self._changed_fields and self.has_loop:
            raise ValidationError("Creating VPN loop")

    @property
    def has_loop(self):
        """
        Check if object creates loop
        """
        if not self.id:
            return False
        p = self.parent
        while p:
            if p.id == self.id:
                return True
            p = p.parent
        return False

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vpn")
