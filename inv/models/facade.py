# ---------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import threading
import operator
from typing import Dict, Optional, Union, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, ObjectIdField
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.main.models.doccategory import category
from noc.core.text import quote_safe_path

id_lock = threading.Lock()


@category
@on_delete_check(
    check=[
        ("inv.ConnectionType", "facade"),
        ("inv.ObjectModel", "front_facade"),
        ("inv.ObjectModel", "rear_facade"),
    ]
)
class Facade(Document):
    meta = {
        "collection": "facades",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.facades",
    }

    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    description = StringField()
    # Image data
    data = StringField(required=True)
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Facade"]:
        return Facade.objects.filter(id=oid).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
        }
        if self.description:
            r["description"] = self.description
        r["data"] = self.data
        return r

    def to_json(self) -> str:
        return to_json(self.json_data, order=["name", "$collection", "uuid", "description", "data"])

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
