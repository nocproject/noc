# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# GIS module database models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import inspect
# NOC modules
from noc.lib import nosql

from layer import Layer


class FontSet(nosql.Document):
    meta = {
        "collection": "noc.gis.fontsets",
        "strict": False,
        "auto_create_index": False
=======
##----------------------------------------------------------------------
## GIS module database models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import inspect
## NOC modules
from noc.lib import nosql

class FontSet(nosql.Document):
    meta = {
        "collection": "noc.gis.fontsets",
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    description = nosql.StringField(required=False)
    fonts = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.name


class Rule(nosql.EmbeddedDocument):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    minscale_zoom = nosql.IntField(required=False)
    maxscale_zoom = nosql.IntField(required=False)
    rule_filter = nosql.StringField(required=False)
    symbolizers = nosql.ListField(nosql.DictField())

    def __unicode__(self):
        return unicode(id(self))

    def __eq__(self, other):
        return (
            self.minscale_zoom == other.minscale_zoom and
            self.maxscale_zoom == other.maxscale_zoom and
            self.rule_filter == other.rule_filter and
            self.symbolizers == other.symbolizers
<<<<<<< HEAD
        )
=======
            )
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Style(nosql.Document):
    meta = {
        "collection": "noc.gis.styles",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    rules = nosql.ListField(nosql.EmbeddedDocumentField(Rule))

    def __unicode__(self):
        return self.name


<<<<<<< HEAD
class _Layer(nosql.Document):
    meta = {
        "collection": "noc.gis.layers",
        "strict": False,
        "auto_create_index": False
=======
class Layer(nosql.Document):
    meta = {
        "collection": "noc.gis.layers",
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
<<<<<<< HEAD
    # srs = nosql.ForeignKeyField(SRS)
=======
    #srs = nosql.ForeignKeyField(SRS)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    styles = nosql.ListField(nosql.StringField())
    datasource = nosql.DictField()

    def __unicode__(self):
        return self.name


class Map(nosql.Document):
    meta = {
        "collection": "noc.gis.maps",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
    # srs = nosql.ForeignKeyField(SRS)
    layers = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.name

    @property
    def active_layers(self):
        """
        Get list of active layers
        :return:
        """
        r = []
        for ln in self.layers:
            l = Layer.objects.filter(name=ln).first()
            if l and l.is_active:
                r += [l]
        return r


class Area(nosql.Document):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

    def __unicode__(self):
        return self.name


class TileCache(nosql.Document):
    meta = {
        "collection": "noc.gis.tilecache",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": [("map", "zoom", "x", "y")]
    }

    map = nosql.ObjectIdField()
    zoom = nosql.IntField(min_value=0, max_value=18)
    x = nosql.IntField(required=True)
    y = nosql.IntField(required=True)
    ready = nosql.BooleanField(default=False)
    last_updated = nosql.DateTimeField()
    data = nosql.BinaryField()

    def __unicode__(self):
        return "%s/%s/%s/%s" % (self.map, self.zoom, self.x, self.y)


class Overlay(nosql.Document):
    meta = {
        "collection": "noc.gis.overlays",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    name = nosql.StringField(required=True)
    gate_id = nosql.StringField(unique=True)
    is_active = nosql.BooleanField(required=True, default=True)
    permission_name = nosql.StringField(required=True)
    overlay = nosql.StringField(required=True)
    config = nosql.DictField()

    _overlay_cache = {}  # name -> Overlay

    def __unicode__(self):
        return self.name

    def get_overlay(self):
        if self.overlay not in self._overlay_cache:
            from noc.gis.overlays.base import OverlayHandler
            m = __import__("noc.gis.overlays.%s" % self.overlay, {}, {}, "*")
            for n in dir(m):
                o = getattr(m, n)
<<<<<<< HEAD
                if (
                    inspect.isclass(o) and o != OverlayHandler and
                    issubclass(o, OverlayHandler)
                ):
=======
                if (inspect.isclass(o) and o != OverlayHandler and
                    issubclass(o, OverlayHandler)):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    self._overlay_cache[self.overlay] = o
                    break
        h = self._overlay_cache[self.overlay]
        return h(**self.config)
