# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GIS module database models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import inspect
# Third-party modules
import six
# NOC modules
from noc.lib import nosql
from .layer import Layer


@six.python_2_unicode_compatible
class FontSet(nosql.Document):
    meta = {
        "collection": "noc.gis.fontsets",
        "strict": False,
        "auto_create_index": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    description = nosql.StringField(required=False)
    fonts = nosql.ListField(nosql.StringField())

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class Rule(nosql.EmbeddedDocument):
    meta = {
        "strict": False,
        "auto_create_index": False
    }
    minscale_zoom = nosql.IntField(required=False)
    maxscale_zoom = nosql.IntField(required=False)
    rule_filter = nosql.StringField(required=False)
    symbolizers = nosql.ListField(nosql.DictField())

    def __str__(self):
        return unicode(id(self))

    def __eq__(self, other):
        return (
            self.minscale_zoom == other.minscale_zoom and
            self.maxscale_zoom == other.maxscale_zoom and
            self.rule_filter == other.rule_filter and
            self.symbolizers == other.symbolizers
        )


@six.python_2_unicode_compatible
class Style(nosql.Document):
    meta = {
        "collection": "noc.gis.styles",
        "strict": False,
        "auto_create_index": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    rules = nosql.ListField(nosql.EmbeddedDocumentField(Rule))

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class _Layer(nosql.Document):
    meta = {
        "collection": "noc.gis.layers",
        "strict": False,
        "auto_create_index": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
    # srs = nosql.ForeignKeyField(SRS)
    styles = nosql.ListField(nosql.StringField())
    datasource = nosql.DictField()

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class Map(nosql.Document):
    meta = {
        "collection": "noc.gis.maps",
        "strict": False,
        "auto_create_index": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
    # srs = nosql.ForeignKeyField(SRS)
    layers = nosql.ListField(nosql.StringField())

    def __str__(self):
        return self.name

    @property
    def active_layers(self):
        """
        Get list of active layers
        :return:
        """
        r = []
        for ln in self.layers:
            lo = Layer.objects.filter(name=ln).first()
            if lo and lo.is_active:
                r += [lo]
        return r


@six.python_2_unicode_compatible
class Area(nosql.Document):
    meta = {
        "strict": False,
        "auto_create_index": False,
        "collection": "noc.gis.areas"
    }

    name = nosql.StringField()
    is_active = nosql.BooleanField(default=True)
    min_zoom = nosql.IntField(default=0)
    max_zoom = nosql.IntField(default=18)
    # (EPSG:4326) coordinates
    SW = nosql.GeoPointField()
    NE = nosql.GeoPointField()
    description = nosql.StringField(required=False)

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class TileCache(nosql.Document):
    meta = {
        "collection": "noc.gis.tilecache",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("map", "zoom", "x", "y")]
    }

    map = nosql.ObjectIdField()
    zoom = nosql.IntField(min_value=0, max_value=18)
    x = nosql.IntField(required=True)
    y = nosql.IntField(required=True)
    ready = nosql.BooleanField(default=False)
    last_updated = nosql.DateTimeField()
    data = nosql.BinaryField()

    def __str__(self):
        return "%s/%s/%s/%s" % (self.map, self.zoom, self.x, self.y)


@six.python_2_unicode_compatible
class Overlay(nosql.Document):
    meta = {
        "collection": "noc.gis.overlays",
        "strict": False,
        "auto_create_index": False
    }

    name = nosql.StringField(required=True)
    gate_id = nosql.StringField(unique=True)
    is_active = nosql.BooleanField(required=True, default=True)
    permission_name = nosql.StringField(required=True)
    overlay = nosql.StringField(required=True)
    config = nosql.DictField()

    _overlay_cache = {}  # name -> Overlay

    def __str__(self):
        return self.name

    def get_overlay(self):
        if self.overlay not in self._overlay_cache:
            from noc.gis.overlays.base import OverlayHandler
            m = __import__("noc.gis.overlays.%s" % self.overlay, {}, {}, "*")
            for n in dir(m):
                o = getattr(m, n)
                if (
                    inspect.isclass(o) and o != OverlayHandler and
                    issubclass(o, OverlayHandler)
                ):
                    self._overlay_cache[self.overlay] = o
                    break
        h = self._overlay_cache[self.overlay]
        return h(**self.config)
