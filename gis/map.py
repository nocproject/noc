# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import pyproj
import geojson
## NOC modules
from noc.gis.models.layer import Layer
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from noc.lib.geo import distance


class Map(object):
    CONDUITS_LAYERS = ["manholes", "cableentries"]

    def __init__(self):
        self.layers = {}
        self.srid_map = {}
        # Database projection
        self.proj = {}
        self.db_proj = self.get_proj("EPSG:4326")
        self.proj["EPSG:900913"] = self.get_proj("EPSG:3857")

    def get_proj(self, srid):
        if isinstance(srid, pyproj.Proj):
            return srid
        ss = self.proj.get(srid)
        if not ss:
            ss = pyproj.Proj(init=srid)
            self.proj[srid] = ss
        return ss

    def get_db_point(self, x, y, srid=None):
        """
        Return GeoJSON Point translated to database projection
        :param x:
        :param y:
        :param srid:
        :return:
        """
        src_srid = self.get_proj(srid) if srid else self.db_proj
        pd = geojson.Point(coordinates=[x, y])
        return self.transform(pd, src_srid, self.db_proj)

    def get_layer(self, name):
        if name in self.layers:
            return self.layers[name]
        layer = Layer.objects.filter(code=name).first()
        if layer:
            self.layers[name] = layer.id
            return self.layers[name]
        raise Exception("Layer not found: %s" % name)

    def get_default_zoom(self, layer, object=None):
        layer = Layer.objects.filter(code=layer).first()
        if not layer:
            return None
        if object is not None:
            zl = object.get_data("geopoint", "zoom")
            if zl:
                return zl
        return layer.default_zoom

    def get_bbox(self, x0, y0, x1, y1, srid):
        src_proj = self.get_proj(srid)
        cx0, cy0 = pyproj.transform(src_proj, self.db_proj, x0, y0)
        cx1, cy1 = pyproj.transform(src_proj, self.db_proj, x1, y1)
        bbox = geojson.Polygon(
            [[[cx0, cy0], [cx1, cy0], [cx1, cy1],
              [cx0, cy1], [cx0, cy0]]]
        )
        return bbox

    def get_layer_objects(self, layer, x0, y0, x1, y1, srid):
        """
        Extract GeoJSON from bounding box
        """
        l = Layer.get_by_code(layer)
        if not l:
            return {}
        bbox = self.get_bbox(x0, y0, x1, y1, srid)
        features = [
            geojson.Feature(
                id=str(d["_id"]),
                geometry=self.transform(d["point"], self.db_proj, srid),
                properties={
                    "object": str(d["_id"]),
                    "label": d.get("name", "")
                }
            )
            for d in Object._get_collection().find({
                "layer": l.id,
                "point": {
                    "$geoWithin": {
                        "$geometry": bbox
                    }
                }
            }, {
                "_id": 1,
                "point": 1,
                "label": 1
            })
        ]
        return geojson.FeatureCollection(features=features, crs=srid)

    def get_conduits_layers(self):
        """
        Returns a list of ids of conduits-related layers
        manholes/cableentries/etc
        """
        if not hasattr(self, "_conduit_layers_ids"):
            self._conduit_layers_ids = Layer.objects.filter(
                code__in=self.CONDUITS_LAYERS).values_list("id")
        return self._conduit_layers_ids

    def transform(self, data, src_srid, dst_srid):
        src = self.get_proj(src_srid)
        dst = self.get_proj(dst_srid)
        if src == dst:
            return data
        if data["type"] == "Point":
            x, y = data["coordinates"]
            data["coordinates"] = pyproj.transform(
                src, dst, x, y)
        elif data["type"] == "LineString":
            data["coordinates"] = [pyproj.transform(src, dst, x, y)
                                   for x, y in data["coordinates"]]
        return data

    def get_connection_layer(self, layer, x0, y0, x1, y1, srid):
        """
        Build line connections
        """
        bbox = self.get_bbox(x0, y0, x1, y1, srid)
        features = [
            geojson.Feature(
                id="-".join(str(c["object"]) for c in d["connection"]),
                geometry=self.transform(d["line"], self.db_proj, srid)
            )
            for d in ObjectConnection._get_collection().find({
                "layer": layer.id,
                "line": {
                    "$geoWithin": {
                        "$geometry": bbox
                    }
                }
            }, {
                "_id": 1,
                "connection": 1,
                "line": 1
            })
        ]
        return geojson.FeatureCollection(features=features, crs=srid)

    def find_nearest(self, point, layers):
        """
        Find and return nearest object
        :param point: GeoJSON Point or tuple of (x, y) or (x, y, srid)
        :param layers: List of layer instances or layer names
        """
        # Normalize point
        if isinstance(point, tuple):
            point = geojson.Point(coordinates=[point[0], point[1]])
            if len(point) == 3:
                point = self.transform(point, point[2], self.db_proj)
        q = {
            "point__near": point
        }
        if isinstance(layers, list):
            q["layer__in"] = layers
        else:
            q["layer"] = layers
        for o in Object.objects.filter(**q)[:1]:
            return o
        return None

    def find_nearest_d(self, point, layers):
        """
        Like find_nearest but return a tuple of (Object, distance)
        """
        if isinstance(point, tuple):
            point = geojson.Point(coordinates=[point[0], point[1]])
            if len(point) == 3:
                point = self.transform(point, point[2], self.db_proj)
        o = self.find_nearest(point, layers)
        if o:
            return o, distance(point, o.point)
        else:
            return None, None

map = Map()
