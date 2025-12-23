# ---------------------------------------------------------------------
# MaintenanceType
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
import bson
import cachetools

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField

# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(check=[("maintenance.Maintenance", "type")])
class MaintenanceType(Document):
    meta = {
        "collection": "noc.maintenancetype",
        "strict": False,
        "auto_create_index": False,
        "legacy_collections": ["noc.maintainancetype"],
    }

    name = StringField(unique=True)
    description = StringField()
    suppress_alarms = BooleanField()
    card_template = StringField()

    _id_cache = cachetools.TTLCache(maxsize=10, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=10, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["MaintenanceType"]:
        return MaintenanceType.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["MaintenanceType"]:
        return MaintenanceType.objects.filter(name=name).first()
