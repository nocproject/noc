# ----------------------------------------------------------------------
# Service Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union
from functools import partial

# Third-party modules
from bson import ObjectId
from pymongo import UpdateOne
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    ReferenceField,
    IntField,
    BooleanField,
    LongField,
    ListField,
    EmbeddedDocumentField,
)
import cachetools

# NOC modules
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_save
from noc.core.bi.decorator import bi_sync
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.inv.models.capsitem import CapsItem
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change


id_lock = Lock()


@Label.match_labels("serviceprofile", allowed_op={"="})
@Label.model
@bi_sync
@change
@on_save
@on_delete_check(check=[("sa.Service", "profile")], clean_lazy_labels="serviceprofile")
class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["labels"],
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    card_title_template = StringField()
    # Short service code for reporting
    code = StringField()
    # FontAwesome glyph
    glyph = StringField()
    # Glyph order in summary
    display_order = IntField(default=100)
    # Show in total summary
    show_in_summary = BooleanField(default=True)
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "sa.ServiceProfile")
    )
    # Auto-assign interface profile when service binds to interface
    interface_profile = ReferenceField(InterfaceProfile)
    # Alarm weight
    weight = IntField(default=0)
    # Capabilities
    caps = ListField(EmbeddedDocumentField(CapsItem))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Service Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ServiceProfile"]:
        return ServiceProfile.objects.filter(id=oid).first()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "interface_profile" in self._changed_fields:
            defer(
                "noc.sa.models.serviceprofile.refresh_interface_profiles",
                key=hash_int(self.id),
                sp_id=str(self.id),
                ip_id=str(self.interface_profile.id) if self.interface_profile else None,
            )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_serviceprofile")

    @classmethod
    def iter_lazy_labels(cls, service_profile: "ServiceProfile"):
        yield f"noc::serviceprofile::{service_profile.name}::="


def refresh_interface_profiles(sp_id, ip_id):
    from .service import Service
    from noc.inv.models.interface import Interface

    svc = [x["_id"] for x in Service._get_collection().find({"profile": sp_id}, {"_id": 1})]
    if not svc:
        return
    collection = Interface._get_collection()
    bulk = []
    bulk += [UpdateOne({"_id": {"$in": svc}}, {"$set": {"profile": ip_id}})]
    collection.bulk_write(bulk, ordered=False)
