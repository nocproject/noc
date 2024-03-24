# ---------------------------------------------------------------------
# PhoneRangeProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from .phonenumberprofile import PhoneNumberProfile

id_lock = Lock()


@on_delete_check(check=[("phone.PhoneRange", "profile")])
class PhoneRangeProfile(Document):
    meta = {"collection": "noc.phonerangeprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    # Default phone number profile
    default_number_profile = PlainReferenceField(PhoneNumberProfile)
    # Cooldown time in days
    # Time when number will be automatically transferred from C to F state
    cooldown = IntField(default=30)
    style = ForeignKeyField(Style)
    workflow = PlainReferenceField(Workflow)

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["PhoneRangeProfile"]:
        return PhoneRangeProfile.objects.filter(id=oid).first()
