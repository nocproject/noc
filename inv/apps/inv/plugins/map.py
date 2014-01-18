# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv map plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin
from noc.gis.map import map
from noc.gis.models.layer import Layer
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
                "fill_color": "#%06x" % l.fill_color
            } for l in Layer.objects.all()
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
        return self.app.render_response(
            map.get_layer_objects(layer, x0, y0, x1, y1, srid),
            content_type="text/json")

    def api_set_geopoint(self, request, id, srid=None, x=None, y=None):
        o = self.app.get_object_or_404(Object, id=id)
        o.set_data("geopoint", "srid", srid)
        o.set_data("geopoint", "x", x)
        o.set_data("geopoint", "y", y)
        o.save()
        return {"status": True}