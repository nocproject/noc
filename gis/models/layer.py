# ---------------------------------------------------------------------
# Map Layer
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
from typing import Any, Dict, Optional, Union

# Third-party modules
import bson
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField, BooleanField
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check

id_lock = Lock()

DEFAULT_ZOOM = 11


@on_delete_check(check=[("inv.Object", "layer"), ("inv.ObjectConnection", "layer")])
class Layer(Document):
    meta = {
        "collection": "noc.layers",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "gis.layers",
    }
    name = StringField(unique=True)
    code = StringField(unique=True)
    uuid = UUIDField(unique=True, binary=True)
    description = StringField(required=False)
    # Visibility
    min_zoom = IntField(min_value=0, max_value=20)
    max_zoom = IntField(min_value=0, max_value=20)
    default_zoom = IntField(min_value=0, max_value=20)
    # z-index. Layers with greater zindex always shown on top
    zindex = IntField(default=0)
    # Point and line symbolizers
    stroke_color = IntField(min_value=0, max_value=0x00FFFFFF)
    fill_color = IntField(min_value=0, max_value=0x00FFFFFF)
    stroke_width = IntField(default=1)
    # Point symbolizer
    point_radius = IntField(default=5)
    point_graphic = StringField(
        choices=[
            (x, x)
            for x in (
                "circle",
                "triangle",
                "cross",
                "x",
                "square",
                "star",
                "diamond",
                "antenna",
                "flag",
            )
        ],
        default="circle",
    )
    # Line symbolizer
    stroke_dashstyle = StringField(
        choices=[(x, x) for x in ("solid", "dash", "dashdot", "longdash", "longdashdot")],
        default="solid",
    )
    # Text symbolizers
    show_labels = BooleanField(default=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Layer"]:
        try:
            return Layer.objects.get(id=oid)
        except Layer.DoesNotExist:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code):
        try:
            return Layer.objects.get(code=code)
        except Layer.DoesNotExist:
            return None

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "code": self.code,
            "uuid": str(self.uuid),
            "min_zoom": self.min_zoom,
            "max_zoom": self.max_zoom,
            "default_zoom": self.default_zoom,
            "zindex": self.zindex,
            "stroke_width": self.stroke_width,
            "stroke_color": self.stroke_color,
            "fill_color": self.fill_color,
            "point_radius": self.point_radius,
            "point_graphic": self.point_graphic,
            "show_labels": self.show_labels,
            "stroke_dashstyle": self.stroke_dashstyle,
        }
        if self.description:
            r["description"] = self.description
        return r

    def to_json(self) -> str:
        return to_json(self.json_data, order=["name", "$collection", "uuid", "description"])

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
