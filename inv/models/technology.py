# ---------------------------------------------------------------------
# Technology
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
import threading
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, BooleanField, LongField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path

id_lock = threading.Lock()


@bi_sync
@on_delete_check(check=[("inv.ResourceGroup", "technology"), ("inv.Protocol", "technology")])
class Technology(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """

    meta = {
        "collection": "technologies",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.technologies",
        "json_unique_fields": ["name"],
    }

    # Group | Name
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    service_model = StringField()
    client_model = StringField()
    single_service = BooleanField(default=False)
    single_client = BooleanField(default=False)
    allow_children = BooleanField(default=False)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Technology"]:
        return Technology.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Technology"]:
        return Technology.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return Technology.objects.filter(name=name).first()

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def to_json(self) -> str:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "single_service": self.single_service,
            "single_client": self.single_client,
            "allow_children": self.allow_children,
        }
        if self.description:
            r["description"] = self.description
        if self.service_model:
            r["service_model"] = self.service_model
        if self.client_model:
            r["client_model"] = self.client_model
        return to_json(
            r,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "service_model",
                "client_model",
                "single_service",
                "single_client",
                "allow_children",
            ],
        )
