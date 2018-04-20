# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pyproj
import geojson
# NOC modules
from noc.gis.models.layer import Layer
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
=======
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
from noc.gis.models.geodata import GeoData
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.geo import distance


class Map(object):
    CONDUITS_LAYERS = ["manholes", "cableentries"]
<<<<<<< HEAD
=======
    POP_LAYERS = ["pop_international", "pop_national", "pop_regional",
                  "pop_core", "pop_aggregation", "pop_access"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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

<<<<<<< HEAD
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
=======
    def set_point(self, object, layer, x, y, srid=None, label=None):
        # Resolve layer
        layer = self.get_layer(layer)
        # Try to find existing point
        p = GeoData.objects.filter(layer=layer, object=object).first()
        if not p:
            p = GeoData(layer=layer, object=object)
        # Set point
        src_srid = self.get_proj(srid) if srid else self.db_proj
        pd = geojson.Point(coordinates=[x, y])
        p.data = self.transform(pd, src_srid, self.db_proj)
        p.label = label
        p.save()

    def delete_point(self, object, layer=None):
        if layer:
            # Resolve layer
            layer = self.get_layer(layer)
            GeoData.objects.filter(object=object, layer=layer).delete()
        else:
            GeoData.objects.filter(object=object).delete()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def get_layer(self, name):
        if name in self.layers:
            return self.layers[name]
        layer = Layer.objects.filter(code=name).first()
        if layer:
<<<<<<< HEAD
            self.layers[name] = layer.id
=======
            self.layers[name] = str(layer.id)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
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
=======
        l = Layer.objects.filter(code=layer).first()
        if not l:
            return {}
        features = []
        bbox = self.get_bbox(x0, y0, x1, y1, srid)
        for d in GeoData.objects.filter(layer=l, data__geo_within=bbox):
            features += [geojson.Feature(
                id=str(d["id"]),
                geometry=self.transform(d["data"], self.db_proj, srid),
                properties={
                    "object": str(d.object.id),
                    "label": d.label.encode("utf-8") if d.label else ""
                }
            )]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
=======
    def get_pop_layers(self):
        """
        Returns a list of ids of pop-related layers
        """
        if not hasattr(self, "_pop_layers_ids"):
            self._pop_layers_ids = Layer.objects.filter(
                code__in=self.POP_LAYERS).values_list("id")
        return self._pop_layers_ids

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def transform(self, data, src_srid, dst_srid):
        src = self.get_proj(src_srid)
        dst = self.get_proj(dst_srid)
        if src == dst:
            return data
        if data["type"] == "Point":
            x, y = data["coordinates"]
            data["coordinates"] = pyproj.transform(
                src, dst, x, y)
<<<<<<< HEAD
        elif data["type"] == "LineString":
            data["coordinates"] = [pyproj.transform(src, dst, x, y)
                                   for x, y in data["coordinates"]]
        return data

    def get_connection_layer(self, layer, x0, y0, x1, y1, srid):
=======
        return data

    def get_connection_layer(self, layers, x0, y0, x1, y1, srid, name,
                             cfilter=None):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        """
        Build line connections
        """
        bbox = self.get_bbox(x0, y0, x1, y1, srid)
<<<<<<< HEAD
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
=======
        # Get all objects from desired layer
        points = {}  # Object.id, point
        lines = set()  # (object1, object2)
        for gd in GeoData.objects.filter(layer__in=layers, data__geo_within=bbox):
            d = self.transform(gd.data, self.db_proj, srid)
            points[str(gd.object.id)] = d["coordinates"]
            # Get all lines connections
            for c, remote, remote_name in gd.object.get_genderless_connections(name):
                if (remote, gd.object) not in lines and (not cfilter or cfilter(c)):
                    lines.add((gd.object, remote))
        # Find and resolve missed points
        missed_points = set()
        for o1, o2 in lines:
            o1_id = str(o1.id)
            if o1_id not in points:
                missed_points.add(o1_id)
            o2_id = str(o2.id)
            if o2_id not in points:
                missed_points.add(o2_id)
        if missed_points:
            for gd in GeoData.objects.filter(
                    layer__in=layers, object__in=missed_points):
                d = self.transform(gd.data, self.db_proj, srid)
                points[gd.object] = d["coordinates"]
        features = []
        for o1, o2 in lines:
            o1_id = str(o1.id)
            o2_id = str(o2.id)
            if o1_id not in points or o2_id not in points:
                continue  # Skip unresolved connection
            ls = geojson.LineString(
                coordinates=[points[o1_id], points[o2_id]]
            )
            features += [geojson.Feature(
                id="%s-%s" % (o1_id, o2_id),
                geometry=ls
            )]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
            "point__near": point
=======
            "data__near": point
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        }
        if isinstance(layers, list):
            q["layer__in"] = layers
        else:
            q["layer"] = layers
<<<<<<< HEAD
        for o in Object.objects.filter(**q)[:1]:
            return o
=======
        for gd in GeoData.objects.filter(**q)[:1]:
            return gd
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return None

    def find_nearest_d(self, point, layers):
        """
<<<<<<< HEAD
        Like find_nearest but return a tuple of (Object, distance)
=======
        Like find_nearest but return a tuple of (GeoData, distance)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        """
        if isinstance(point, tuple):
            point = geojson.Point(coordinates=[point[0], point[1]])
            if len(point) == 3:
                point = self.transform(point, point[2], self.db_proj)
<<<<<<< HEAD
        o = self.find_nearest(point, layers)
        if o:
            return o, distance(point, o.point)
=======
        gd = self.find_nearest(point, layers)
        if gd:
            return gd, distance(point, gd.data)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        else:
            return None, None

map = Map()
