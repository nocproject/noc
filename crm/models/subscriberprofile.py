# ----------------------------------------------------------------------
# Subscriber Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, IntField, LongField, BooleanField
import cachetools

# NOC models
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@change
@on_delete_check(check=[("crm.Subscriber", "profile")])
class SubscriberProfile(Document):
    meta = {"collection": "noc.subscriberprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    workflow = PlainReferenceField(Workflow)
    # FontAwesome glyph
    glyph = StringField()
    # Glyph order in summary
    display_order = IntField(default=100)
    # Show in total summary
    show_in_summary = BooleanField(default=True)
    # Labels
    labels = ListField(StringField())
    # Alarm weight
    weight = IntField(default=0)
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
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SubscriberProfile"]:
        return SubscriberProfile.objects.filter(id=oid).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_subscriber")
