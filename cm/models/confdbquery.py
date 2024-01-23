# ----------------------------------------------------------------------
# ConfDBQuery model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
from typing import Optional, Union
import operator
import os

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    ListField,
    EmbeddedDocumentField,
)
import cachetools

# NOC modules
from noc.core.ip import IP
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.sa.interfaces.base import StringParameter, IntParameter, BooleanParameter


class IPParameter(object):
    def clean(self, value):
        return IP.prefix(value)


id_lock = threading.Lock()
TYPE_MAP = {
    "str": StringParameter(),
    "int": IntParameter(),
    "bool": BooleanParameter(),
    "ip": IPParameter(),
}


class ConfDBQueryParam(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField()
    type = StringField(choices=["str", "int", "bool", "ip"])
    default = StringField()
    description = StringField()

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "default": self.default,
        }

    def get_parameter(self):
        return TYPE_MAP[self.type]


@on_delete_check(
    check=[
        ("cm.InterfaceValidationPolicy", "filter_query"),
        ("cm.InterfaceValidationPolicy", "rules.query"),
        ("cm.InterfaceValidationPolicy", "rules.filter_query"),
        ("cm.ObjectValidationPolicy", "filter_query"),
        ("cm.ObjectValidationPolicy", "rules.query"),
        ("cm.ObjectValidationPolicy", "rules.filter_query"),
    ]
)
class ConfDBQuery(Document):
    meta = {
        "collection": "confdbqueries",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "cm.confdbqueries",
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    source = StringField()
    params = ListField(EmbeddedDocumentField(ConfDBQueryParam))
    allow_object_filter = BooleanField(default=False)
    allow_interface_filter = BooleanField(default=False)
    allow_object_validation = BooleanField(default=False)
    allow_interface_validation = BooleanField(default=False)
    allow_object_classification = BooleanField(default=False)
    allow_interface_classification = BooleanField(default=False)
    require_raw = BooleanField(default=False)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ConfDBQuery"]:
        return ConfDBQuery.objects.filter(id=oid).first()

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def query(self, engine, **kwargs):
        """
        Run query against ConfDB engine
        :param engine: ConfDB engine
        :param kwargs: Optional arguments
        :return:
        """
        params = kwargs.copy()
        for p in self.params:
            params[p.name] = p.get_parameter().clean(params.get(p.name, p.default))
        for ctx in engine.query(self.source, **params):
            yield ctx

    def any(self, engine, **kwargs):
        """
        Run query agains ConfDB engine and return True if any result found
        :param engine: ConfDB engine
        :param kwargs: Optional arguments
        :return: True if any result found
        """
        return engine.any(self.source, **kwargs)

    def to_json(self) -> str:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "source": self.source,
            "params": [p.to_json() for p in self.params],
            "allow_object_filter": self.allow_object_filter,
            "allow_interface_filter": self.allow_interface_filter,
            "allow_object_validation": self.allow_object_validation,
            "allow_interface_validation": self.allow_interface_validation,
            "allow_object_classification": self.allow_object_classification,
            "allow_interface_classification": self.allow_interface_classification,
            "require_raw": self.require_raw,
        }
        if self.description:
            r["description"] = self.description
        return to_json(
            r,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "source",
                "params",
                "allow_object_filter",
                "allow_interface_filter",
                "allow_object_validation",
                "allow_interface_validation",
                "allow_object_classification",
                "allow_interface_classification",
                "require_raw",
            ],
        )
