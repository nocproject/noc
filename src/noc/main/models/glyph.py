# ----------------------------------------------------------------------
# Glyph Collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Future imports
from __future__ import annotations

# Python modules
import operator
from pathlib import Path
from threading import Lock
from typing import Any

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document
from mongoengine.fields import IntField, StringField, UUIDField

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json

id_lock = Lock()


@on_delete_check(
    check=[
        ("project.Project", "shape_overlay_glyph"),
        ("sa.ManagedObject", "shape_overlay_glyph"),
        ("sa.ManagedObject", "glyph"),
        ("sa.ManagedObjectProfile", "shape_overlay_glyph"),
        ("sa.ManagedObjectProfile", "glyph"),
        ("inv.ObjectModel", "glyph"),
        ("inv.CPEProfile", "glyph"),
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
    code = IntField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: str | bson.ObjectId) -> Glyph | None:
        return Glyph.objects.filter(id=oid).first()

    @property
    def json_data(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": str(self.uuid),
            "code": self.code,
        }

    def to_json(self) -> str:
        return to_json(self.json_data, order=["name", "$collection", "uuid", "code"])

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    @property
    def css_class(self) -> str | None:
        """
        Generate CSS class
        """
        return f"gf {self.name}"
