# ---------------------------------------------------------------------
# PhoneNumberProfile model
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
from mongoengine.fields import StringField
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[("phone.PhoneNumber", "profile"), ("phone.PhoneRangeProfile", "default_number_profile")]
)
class PhoneNumberProfile(Document):
    meta = {"collection": "noc.phonenumberprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style)
    workflow = PlainReferenceField(Workflow)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["PhoneNumberProfile"]:
        return PhoneNumberProfile.objects.filter(id=oid).first()
