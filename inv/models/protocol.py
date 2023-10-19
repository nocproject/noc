# ----------------------------------------------------------------------
# Protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import operator
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Iterable, List, Any, Dict

# Third-party modules
import cachetools
from mongoengine.queryset.base import NULLIFY
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    EmbeddedDocumentListField,
    UUIDField,
    DynamicField,
    BooleanField,
    ListField,
    ReferenceField,
)
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.inv.models.technology import Technology
from noc.core.protocoldiscriminators.base import BaseDiscriminatorSource
from noc.core.protocoldiscriminators.loader import loader

id_lock = Lock()


@dataclass(frozen=True)
class ProtocolVariant(object):
    protocol: "Protocol"
    direction: str = "*"
    discriminator: Optional[str] = None
    data: Optional[Dict[str, str]] = None

    def __str__(self) -> str:
        return self.code

    @property
    def code(self) -> str:
        if not self.discriminator and self.direction == "*":
            return self.protocol.code
        elif not self.discriminator:
            return f"{self.protocol.code}::{self.direction}"
        else:
            return f"{self.protocol.code}::{self.discriminator}::{self.direction}"

    @classmethod
    def get_by_code(cls, code: str) -> "ProtocolVariant":
        p_code, *x = code.split("::")
        protocol = Protocol.get_by_code(p_code)
        if not protocol:
            raise ValueError(f"Unknown protocol code: {p_code}")
        if not x:
            return ProtocolVariant(protocol)
        elif len(x) == 1:
            return ProtocolVariant(protocol, x[0])
        elif len(x) > 2:
            raise ValueError(f"Unknown variant format: {code}")
        return ProtocolVariant(protocol, x[1], x[0])


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


class DiscriminatorAttr(EmbeddedDocument):
    code: str = StringField()
    data: List["ProtocolAttr"] = EmbeddedDocumentListField(ProtocolAttr)

    def __str__(self):
        return self.code

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"code": self.code, "data": [d.json_data for d in self.data]}


@bi_sync
@on_delete_check(check=[("inv.ObjectModel", "connections__protocols__protocol")])
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
    connection_schema = StringField(
        choices=[
            ("UNI", "Unidirectional"),
            ("BO", "Bidirectional over One Connection"),
            ("BD", "Bidirectional over Differ Connection"),
        ],
        default="BD",
    )
    discriminator_source = StringField(default=None)
    discriminators: List[DiscriminatorAttr] = EmbeddedDocumentListField(DiscriminatorAttr)
    # transport_protocols = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
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
            del cls._id_cache[str(id),]  # Tuple
        except KeyError:
            pass

    def get_data(self, interface: str, key: str, **kwargs) -> Any:
        for item in self.data:
            if item.interface == interface and item.attr == key:
                return item.value
        return None

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "code": self.code,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "technology__name": self.technology.name,
            "connection_schema": self.connection_schema,
            "data": [c.json_data for c in self.data],
        }
        if self.discriminators:
            r["discriminators"] = [d.json_data for d in self.discriminators]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "code", "$collection", "uuid", "description", "technology", "data"],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def get_variant_by_code(cls, code: str) -> "ProtocolVariant":
        """
        Return protocol variant by code

        :param code: Protocol Variant code
        """
        return ProtocolVariant.get_by_code(code)

    def iter_protocol_variants(self) -> Iterable[ProtocolVariant]:
        """
        @todo combinations
        """
        yield ProtocolVariant(self)
        if self.connection_schema != "BO":
            yield ProtocolVariant(self, ">")
            yield ProtocolVariant(self, "<")
        if not self.discriminator_source:
            return
        ds = self.get_discriminator_source()
        for code in ds:
            yield ProtocolVariant(self, "<", code)

    def get_discriminator_source(
        self, data: Optional[List[ProtocolAttr]] = None
    ) -> Optional[BaseDiscriminatorSource]:
        ds = loader[self.discriminator_source]
        return ds(self, data)
