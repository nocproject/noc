# ----------------------------------------------------------------------
# Subscriber
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
from mongoengine.fields import StringField, ListField, LongField
import cachetools

# NOC modules
from .subscriberprofile import SubscriberProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@on_delete_check(check=[("inv.Channel", "subscriber"), ("sa.Service", "subscriber")])
@workflow
class Subscriber(Document):
    meta = {
        "collection": "noc.subscribers",
        "indexes": ["name", "labels", "effective_labels"],
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField()
    description = StringField()
    profile = PlainReferenceField(SubscriberProfile)
    state = PlainReferenceField(State)
    # Main address
    address = StringField()
    # Technical contacts
    tech_contact_person = StringField()
    tech_contact_phone = StringField()
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Subscriber"]:
        return Subscriber.objects.filter(id=oid).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_subscriber")
