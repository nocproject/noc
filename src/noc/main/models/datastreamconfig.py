# ----------------------------------------------------------------------
# DataStreamConfig Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Future imports
from __future__ import annotations

# Python modules
import operator
from collections.abc import Callable, Iterable
from threading import Lock
from typing import Any

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import BooleanField, EmbeddedDocumentListField, StringField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.main.models.handler import Handler

id_lock = Lock()


class DSFormat(EmbeddedDocument):
    name = StringField()
    is_active = BooleanField()
    handler = PlainReferenceField(Handler)
    role = StringField()

    def __str__(self):
        return self.name


class DataStreamConfig(Document):
    meta = {"collection": "datastreamconfigs", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    formats = EmbeddedDocumentListField(DSFormat)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: str | ObjectId) -> DataStreamConfig | None:
        return DataStreamConfig.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> DataStreamConfig | None:
        return DataStreamConfig.objects.filter(name=name).first()

    def iter_formats(
        self,
    ) -> Iterable[tuple[str, Callable[[dict[str, Any]], Iterable[dict[str, Any]]]]]:
        for fmt in self.formats:
            if fmt.is_active:
                handler = fmt.handler.get_handler()
                if handler:
                    yield fmt.name, handler
