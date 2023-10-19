# ----------------------------------------------------------------------
# Protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import operator
import datetime
import logging
from threading import Lock
from typing import Optional, Iterable, List, Any, Dict

# Third-party modules
import cachetools
from pymongo import UpdateOne, ReadPreference
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, LongField, EmbeddedDocumentListField, UUIDField, DynamicField, BooleanField
from mongoengine.errors import ValidationError

# NOC modules
from noc.models import get_model, is_document
from noc.core.mongo.fields import PlainReferenceField
from noc.inv.models.technology import Technology
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


class ProtocolAttr(EmbeddedDocument):
    interface = StringField()
    attr = StringField()
    value = DynamicField()

    def __str__(self):
        return f"{self.interface}.{self.attr} = {self.value}"

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "interface": self.interface,
            "attr": self.attr,
            "value": self.value,
        }


@bi_sync
@on_delete_check(check=[("inv.ObjectModel", "connection_rule")])
class Protocol(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """

    meta = {
        "collection": "protocols",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["code"],
        "json_collection": "inv.protocols",
        "json_unique_fields": ["code", "uuid"],
    }

    #
    name = StringField()
    code = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    technology: "Technology" = PlainReferenceField(Technology)
    data: List["ProtocolAttr"] = EmbeddedDocumentListField(ProtocolAttr)
    connection_schema = StringField(choices=[
        ("UNI", "Unidirectional"),
        ("BO", "Bidirectional over One Connection"),
        ("BD", "Bidirectional over Differ Connection"),
    ], default="BD")
    extend_discriminator = BooleanField(default=False)
    # For
    # use_helper
    # helper = StringField()

    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid):
        return Protocol.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id):
        return Protocol.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code):
        return Protocol.objects.filter(code=code).first()

    @classmethod
    def _reset_caches(cls, id):
        try:
            del cls._id_cache[
                str(id),
            ]  # Tuple
        except KeyError:
            pass

    def get_data(self, interface: str, key: str, **kwargs) -> Any:
        for item in self.data:
            if item.interface == interface and item.attr == key:
                return item.value
        return None

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "code": self.code,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "technology__name": self.technology.name,
            "data": [c.json_data for c in self.data],
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data, order=["name", "code", "$collection", "uuid", "description", "technology", "data"]
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
