# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
## Third-party modules
from vectorformats.Formats.Django import Django as vfDjango
from vectorformats.Formats.GeoJSON import GeoJSON as vfGeoJSON
## NOC modules
from noc.gis.models.layer import Layer
from noc.gis.models.geodata import GeoData
from noc.gis.models.srs import SRS


class Map(object):
    CONDUITS_LAYERS = ["manholes", "cableentries"]

    def __init__(self):
        self.layers = {}
        self.srid_map = {}
        self.srid = SpatialReference("EPSG:4326")

    def set_point(self, object, layer, x, y, srid=None, label=None):
        # Convert object to ObjectId
        if hasattr(object, "id"):
            object = object.id
        object = str(object)
        # Resolve layer
        layer = self.get_layer(layer)
        # Resolve SRS
        if srid:
            srid = self.get_srid(srid)
        # Try to find existing point
        try:
            p = GeoData.objects.get(layer=layer, object=object)
        except GeoData.DoesNotExist:
            p = GeoData(layer=layer, object=object)
        p.data = Point(x, y, srid=srid)
        p.label = label
        p.save()

    def delete_point(self, object, layer=None):
        # Convert object to ObjectId
        if hasattr(object, "id"):
            object = object.id
        object = str(object)
        if layer:
            # Resolve layer
            layer = self.get_layer(layer)
            GeoData.objects.filter(object=object, layer=layer).delete()
        else:
            GeoData.objects.filter(object=object).delete()

    def get_layer(self, name):
        if name in self.layers:
            return self.layers[name]
        layer = Layer.objects.filter(code=name).first()
        if layer:
            self.layers[name] = str(layer.id)
            return self.layers[name]
        raise Exception("Layer not found: %s" % name)

    def get_srid(self, srid):
        if isinstance(srid, basestring):
            if srid in self.srid_map:
                return self.srid_map[srid]
            auth_name, auth_srid = srid.split(":")
            srs = SRS.objects.get(
                auth_name=auth_name, auth_srid=int(auth_srid))
            self.srid_map[srid] = srs.srid
            return srs.srid
        else:
            return int(srid)

    def get_default_zoom(self, layer, object=None):
        layer = Layer.objects.filter(code=layer).first()
        if not layer:
            return None
        if object is not None:
            zl = object.get_data("geopoint", "zoom")
            if zl:
                return zl
        return layer.default_zoom

    def get_layer_objects(self, layer, x0, y0, x1, y1, srid):
        """
        Extract GeoJSON from bounding box
        """
        l = Layer.objects.filter(code=layer).first()
        if not l:
            return {}
        # Build bounding box
        dst_srid = SpatialReference(srid)
        from_transform = CoordTransform(
            dst_srid,
            self.srid
        )
        bbox = Polygon.from_bbox((x0, y0, x1, y1))
        bbox.srid = dst_srid.srid
        bbox.transform(from_transform)
        # Seed result
        qs = GeoData.objects.filter(layer=l.id, data__intersects=bbox).transform(dst_srid.srid)
        dj = vfDjango(geodjango="data", properties=["object", "label"])
        gj = vfGeoJSON()
        gj.crs = srid
        return gj.encode(dj.decode(qs))

    def get_conduits_layers(self):
        """
        Returns a list of ids of conduits-related layers
        manholes/cableentries/etc
        """
        if not hasattr(self, "_conduit_layers_ids"):
            self._conduit_layers_ids = Layer.objects.filter(
                code__in=self.CONDUITS_LAYERS).values_list("id")
        return self._conduit_layers_ids


map = Map()
