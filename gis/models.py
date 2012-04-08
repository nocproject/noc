# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GIS module database models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import inspect
## Django modules
from django.db import models
## NOC modules
from noc.lib import nosql


class SRS(models.Model):
    """
    PostGIS spatial reference system
    """
    class Meta:
        verbose_name = "SRS"
        verbose_name_plural = "SRS"
        db_table = "spatial_ref_sys"

    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, null=True, blank=True)
    auth_srid = models.IntegerField(null=True, blank=True)
    proj4text = models.CharField(max_length=2048, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.srid)

    @property
    def full_id(self):
        """
        Get full SRS ID in form of <AUTH>:<ID>
        :return:
        :rtype: str
        """
        return "%s:%d" % (self.auth_name, self.auth_srid)


class FontSet(nosql.Document):
    meta = {
        "collection": "noc.gis.fontsets",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    description = nosql.StringField(required=False)
    fonts = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.name


class Rule(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
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
            )


class Style(nosql.Document):
    meta = {
        "collection": "noc.gis.styles",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    rules = nosql.ListField(nosql.EmbeddedDocumentField(Rule))

    def __unicode__(self):
        return self.name


class Layer(nosql.Document):
    meta = {
        "collection": "noc.gis.layers",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
    srs = nosql.ForeignKeyField(SRS)
    styles = nosql.ListField(nosql.StringField())
    datasource = nosql.DictField()

    def __unicode__(self):
        return self.name


class Map(nosql.Document):
    meta = {
        "collection": "noc.gis.maps",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=True)
    is_active = nosql.BooleanField(default=True)
    srs = nosql.ForeignKeyField(SRS)
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
        "allow_inheritance": False,
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
        "allow_inheritance": False,
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
        "allow_inheritance": False
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
                if (inspect.isclass(o) and o != OverlayHandler and
                    issubclass(o, OverlayHandler)):
                    self._overlay_cache[self.overlay] = o
                    break
        h = self._overlay_cache[self.overlay]
        return h(**self.config)
