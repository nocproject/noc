# ----------------------------------------------------------------------
# Font Collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from typing import Any, Dict, Optional, Union

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField
import cachetools
import bson

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(check=[("main.Glyph", "font")])
class Font(Document):
    meta = {
        "collection": "fonts",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.fonts",
    }
    name = StringField(unique=True)
    uuid = UUIDField(unique=True, binary=True)
    font_family = StringField()
    description = StringField(required=False)
    stylesheet_href = StringField(required=False)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Font"]:
        return Font.objects.filter(id=oid).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": str(self.uuid),
            "font_family": self.font_family,
        }
        if self.description:
            r["description"] = self.description
        if self.stylesheet_href:
            r["stylesheet_href"] = self.stylesheet_href
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data, order=["name", "$collection", "uuid", "font_family", "description"]
        )

    def get_json_path(self) -> str:
        return "%s.json" % quote_safe_path(self.name)
