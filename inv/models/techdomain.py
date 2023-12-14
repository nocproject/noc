# ----------------------------------------------------------------------
# TechDomain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Dict, Any
import operator

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, LongField, ListDocumentField, UUIDField

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path

id_lock = Lock()


class DiscriminatorItem(EmbeddedDocument):
    """
    Tech domain discriminator.

    Attributes:
        name: Discriminator name.
        description: Discriminator description.
    """

    name = StringField()
    description = StringField()

    def __str__(self) -> str:
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r: Dict[str, Any] = {"name": self.name}
        if self.description:
            r["description"] = self.description
        return r


@bi_sync
@on_delete_check(check=[])
class TechDomain(Document):
    """
    Technological Domain.

    Represents a single techology which
    provides endpoints to the channels
    and hides an internal structure.

    Attributes:
        name: Human-readable name.
        code: Unique code.
        uuid: UUID.
        description: Optional description.
        discriminators: List of available discriminators.
        bi_id: Bi-encoded id.
    """

    meta = {
        "collection": "techdomains",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.techdomains",
    }

    name = StringField(unique=True)
    code = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    discriminators = ListDocumentField(DiscriminatorItem)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: ObjectId) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(code=code).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r: Dict[str, Any] = {
            "name": self.name,
            "code": self.code,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
        }
        if self.discriminators:
            r["discriminators"] = [d.json_data for d in self.discriminators]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "code", "$collection", "uuid", "description"],
        )

    def get_json_path(self) -> str:
        return f"{quote_safe_path(self.code)}.json"
