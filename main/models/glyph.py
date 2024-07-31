# ----------------------------------------------------------------------
# Glyph Collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
from typing import Any, Dict, Optional, Union

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField
import cachetools
import bson

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from .font import Font

id_lock = Lock()


@on_delete_check(
    check=[
        ("project.Project", "shape_overlay_glyph"),
        ("sa.ManagedObject", "shape_overlay_glyph"),
        ("sa.ManagedObjectProfile", "shape_overlay_glyph"),
        ("inv.ObjectModel", "glyph"),
    ]
)
class Glyph(Document):
    meta = {
        "collection": "glyphs",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.glyphs",
    }
    name = StringField(unique=True)
    uuid = UUIDField(unique=True, binary=True)
    font = PlainReferenceField(Font)
    code = IntField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Glyph"]:
        return Glyph.objects.filter(id=oid).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": str(self.uuid),
            "font__name": self.font.name,
            "code": self.code,
        }

    def to_json(self) -> str:
        return to_json(self.json_data, order=["name", "$collection", "uuid", "font__name", "code"])

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def css_class(self) -> Optional[str]:
        """
        Generate CSS class
        """
        if self.font.name == "FontAwesome":
            n = self.name.split("|")[-1].strip()
            return f"fa fa-{n}"
        return None
