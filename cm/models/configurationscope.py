# ----------------------------------------------------------------------
# Configuration Scope model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
import os

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    EmbeddedDocumentListField,
)
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check


id_lock = threading.Lock()


@on_delete_check(check=[("cm.ConfigurationParam", "scopes__scope")])
class ConfigurationScope(Document):
    meta = {
        "collection": "configurationscopes",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "cm.configurationscopes",
        "json_unique_fields": ["name", "uuid"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    helper = StringField(default=None, required=False)
    model_id = StringField(required=False)
    # helper_params = EmbeddedDocumentListField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ConfigurationScope.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return ConfigurationScope.objects.filter(name=name).first()

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def to_json(self) -> str:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
        }
        if self.description:
            r["description"] = self.description
        if self.model_id:
            r["model_id"] = self.model_id
        if self.helper:
            r["helper"] = self.helper
            r["helper_params"] = [p.to_json() for p in self.helper_params]
        return to_json(
            r,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "model_id",
                "helper",
                "helper_params",
            ],
        )
