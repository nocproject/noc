# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map Layer
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, IntField,
                                BooleanField)
## NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path


class Layer(Document):
    meta = {
        "collection": "noc.layers",
        "allow_inheritance": False,
        "json_collection": "gis.layers"
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
    # Line symbolizer
    stroke_dashstyle = StringField(choices=[
        "solid", "dash", "dashdot", "longdash",
        "longdashdot"], default="solid")
    # Text symbolizers
    show_labels = BooleanField(default=True)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
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
            "show_labels": self.show_labels,
            "stroke_dashstyle": self.stroke_dashstyle
        }
        if self.description:
            r["description"] = self.description
        return r

    def to_json(self):
        return to_json(self.json_data, order=["name", "uuid", "description"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
