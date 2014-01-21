# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv map plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.gis.geos import Polygon, LineString
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
## Third-party modules
from vectorformats.Formats.GeoJSON import GeoJSON
from vectorformats.Feature import Feature
## NOC modules
from base import InvPlugin
from noc.gis.map import map
from noc.gis.models.layer import Layer
from noc.gis.models.geodata import GeoData
from noc.inv.models.object import Object
from noc.sa.interfaces.base import StringParameter, FloatParameter


class MapPlugin(InvPlugin):
    name = "map"
    js = "NOC.inv.inv.plugins.map.MapPanel"

    def init_plugin(self):
        super(MapPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_get_layer" % self.name,
            self.api_get_layer,
            url="^plugin/%s/layers/(?P<layer>\S+)/$" % self.name,
            method=["GET"]
        )
        self.add_view(
            "api_plugin_%s_object_data" % self.name,
            self.api_object_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/object_data/" % self.name,
            method=["GET"]
        )
        self.add_view(
            "api_plugin_%s_set_geopoint" % self.name,
            self.api_set_geopoint,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/set_geopoint/" % self.name,
            method=["POST"],
            validate={
                "srid": StringParameter(),
                "x": FloatParameter(),
                "y": FloatParameter()
            }
        )

    def get_parent(self, o):
        """
        Find parent object with geopoint
        """
        p = o.container
        while p:
            p = Object.objects.filter(id=p).first()
            if not p:
                return
            if p.get_data("geopoint", "x") and p.get_data("geopoint", "y"):
                return p
            p = p.container

    def get_data(self, request, o):
        layers = [
            {
                "name": l.name,
                "code": l.code,
                "min_zoom": l.min_zoom,
                "max_zoom": l.max_zoom,
                "stroke_color": "#%06x" % l.stroke_color,
                "fill_color": "#%06x" % l.fill_color,
                "stroke_width": l.stroke_width,
                "point_radius": l.point_radius,
                "show_labels": l.show_labels,
                "stroke_dashstyle": l.stroke_dashstyle
            } for l in Layer.objects.order_by("zindex")
        ]
        srid = o.get_data("geopoint", "srid")
        x = o.get_data("geopoint", "x")
        y = o.get_data("geopoint", "y")
        if x is None or y is None or not srid:
            p = self.get_parent(o)
            if p:
                srid = p.get_data("geopoint", "srid")
                x = p.get_data("geopoint", "x")
                y = p.get_data("geopoint", "y")
        # @todo: Coordinates transform

        return {
            "id": str(o.id),
            "zoom": map.get_default_zoom(
                o.get_data("geopoint", "layer"),
                object=o
            ),
            "x": x,
            "y": y,
            "layer": o.get_data("geopoint", "layer"),
            "layers": layers
        }

    def api_get_layer(self, request, layer):
        bbox = request.GET["bbox"].split(",")
        x0 = float(bbox[0])
        y0 = float(bbox[1])
        x1 = float(bbox[2])
        y1 = float(bbox[3])
        srid = bbox[4]
        if layer == "conduits":
            builder = self.get_conduits_layer
        else:
            builder = map.get_layer_objects
        return self.app.render_response(
            builder(layer, x0, y0, x1, y1, srid),
            content_type="text/json")

    def api_set_geopoint(self, request, id, srid=None, x=None, y=None):
        o = self.app.get_object_or_404(Object, id=id)
        o.set_data("geopoint", "srid", srid)
        o.set_data("geopoint", "x", x)
        o.set_data("geopoint", "y", y)
        o.save()
        return {"status": True}

    def api_object_data(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        return {
            "id": str(o.id),
            "name": o.name,
            "model": o.model.name
        }

    def get_conduits_layer(self, layer, x0, y0, x1, y1, srid):
        """
        Build conduits layer
        """
        manholes_layer = Layer.objects.filter(code="manholes").first()
        if not manholes_layer:
            return {}
        layers = [manholes_layer.id]
        conduits = {}  # id ->
        # Build bounding box
        dst_srid = SpatialReference(srid)
        from_transform = CoordTransform(
            dst_srid,
            map.srid
        )
        bbox = Polygon.from_bbox((x0, y0, x1, y1))
        bbox.srid = dst_srid.srid
        bbox.transform(from_transform)
        # Get all objects from *manholes* layer
        points = {}  # Object.id, point
        conduits = set()  # (object1, object2)
        for gd in GeoData.objects.filter(
                layer__in=layers, data__intersects=bbox
        ).transform(dst_srid.srid):
            object = Object.objects.get(id=gd.object)
            points[str(object.id)] = gd.data
            # Get all conduits connections
            for c, remote, remote_name in object.get_genderless_connections("conduits"):
                if (remote, object) not in conduits:
                    conduits.add((object, remote))
        # Find and resolve missed points
        missed_points = set()
        for o1, o2 in conduits:
            o1_id = str(o1.id)
            if o1_id not in points:
                missed_points.add(o1_id)
            o2_id = str(o2.id)
            if o2_id not in points:
                missed_points.add(o2_id)
        if missed_points:
            for gd in GeoData.objects.filter(
                    layer__in=layers, objects__in=missed_points
            ).transform(dst_srid.srid):
                points[gd.object] = gd.data
        cdata = []
        for o1, o2 in conduits:
            o1_id = str(o1.id)
            o2_id = str(o2.id)
            if o1_id not in points or o2_id not in points:
                continue  # Skip unresolved conduit
            ls = LineString(points[o1_id], points[o2_id])
            f = Feature(len(cdata))
            f.geometry = {
                "type": ls.geom_type,
                "coordinates": ls.coords
            }
            cdata += [f]
        gj = GeoJSON()
        gj.crs = srid
        return gj.encode(cdata)
