# ----------------------------------------------------------------------
# DataStreamConfig Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, ListField, EmbeddedDocumentField
from typing import Union, Optional, Iterable, Dict, Any, Callable, Tuple
from bson import ObjectId
import cachetools

# NOC modules
from noc.main.models.handler import Handler
from noc.core.mongo.fields import PlainReferenceField

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
    formats = ListField(EmbeddedDocumentField(DSFormat))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["DataStreamConfig"]:
        return DataStreamConfig.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["DataStreamConfig"]:
        return DataStreamConfig.objects.filter(name=name).first()

    def iter_formats(
        self,
    ) -> Iterable[Tuple[str, Callable[[Dict[str, Any]], Iterable[Dict[str, Any]]]]]:
        for fmt in self.formats:
            if fmt.is_active:
                handler = fmt.handler.get_handler()
                if handler:
                    yield fmt.name, handler
