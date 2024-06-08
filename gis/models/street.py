# ---------------------------------------------------------------------
# Street object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
import bson
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DictField,
    BooleanField,
    DateTimeField,
    ReferenceField,
    LongField,
)
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text
from .division import Division
from noc.main.models.remotesystem import RemoteSystem
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


@bi_sync
@on_delete_check(check=[("gis.Address", "street")])
class Street(Document):
    meta = {
        "collection": "noc.streets",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "data", "remote_id"],
    }
    #
    parent = PlainReferenceField(Division)
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Additional data
    # Depends on importer
    data = DictField()
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    _id_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Street"]:
        return Street.objects.filter(id=oid).first()

    def __str__(self):
        if self.short_name:
            return "%s, %s" % (self.name, self.short_name)
        else:
            return self.name

    @property
    def full_path(self):
        if not self.parent:
            return ""
        r = [self.parent.full_path, smart_text(self)]
        return " | ".join(r)
