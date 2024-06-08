# ---------------------------------------------------------------------
# EscalationProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Union
import operator
from threading import Lock

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
from bson import ObjectId
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.models.escalationpolicy import EscalationPolicy

id_lock = Lock()


@on_delete_check(
    check=[
        ("fm.Escalation", "profile"),
    ]
)
class EscalationProfile(Document):
    meta = {"collection": "escalationprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    default_escalation_policy = StringField(
        choices=[x[0] for x in EscalationPolicy.get_choices()], default="root"
    )
    delay = IntField()
    # Caches
    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(self, oid: Union[str, ObjectId]) -> Optional["EscalationProfile"]:
        return EscalationProfile.objects.filter(id=oid).first()
