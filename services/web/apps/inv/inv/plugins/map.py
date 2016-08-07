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
from noc.gis.models.layerusersettings import LayerUserSettings
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.sa.interfaces.base import (StringParameter, FloatParameter,
                                    BooleanParameter, DocumentParameter,
                                    UnicodeParameter)


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
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/object_data/$" % self.name,
            method=["GET"]
        )
        self.add_view(
            "api_plugin_%s_set_geopoint" % self.name,
            self.api_set_geopoint,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/set_geopoint/$" % self.name,
            method=["POST"],
            validate={
                "srid": StringParameter(),
                "x": FloatParameter(),
                "y": FloatParameter()
            }
        )
        self.add_view(
            "api_plugin_%s_set_layer_visibility" % self.name,
            self.api_set_layer_visibility,
            url="^plugin/%s/layer_visibility/$" % self.name,
            method=["POST"],
            validate={
                "layer": StringParameter(),
                "status": BooleanParameter()
            }
        )

        self.add_view(
            "api_plugin_%s_create" % self.name,
            self.api_create,
            url="^plugin/%s/$" % self.name,
            method=["POST"],
            validate={
                "model": DocumentParameter(ObjectModel),
                "name": UnicodeParameter(),
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
                "stroke_dashstyle": l.stroke_dashstyle,
                "point_graphic": l.point_graphic,
                "is_visible": LayerUserSettings.is_visible_by_user(request.user, l)
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
        # Feed result
        return {
            "id": str(o.id),
            "zoom": map.get_default_zoom(
                o.get_data("geopoint", "layer"),
                object=o
            ),
            "x": x,
            "y": y,
            "layer": o.get_data("geopoint", "layer"),
            "layers": layers,
            "add_menu": self.get_add_menu()
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
        elif layer.startswith("pop_link"):
            builder = self.get_pop_links_layer
        else:
            builder = map.get_layer_objects
        return builder(layer, x0, y0, x1, y1, srid)

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
        l = Layer.get_by_code("conduits")
        return map.get_connection_layer(
            l, x0, y0, x1, y1, srid
        )

    def get_pop_links_layer(self, layer, x0, y0, x1, y1, srid):
        l = Layer.get_by_code(layer)
        return map.get_connection_layer(
            l, x0, y0, x1, y1, srid
        )

    def api_set_layer_visibility(self, request, layer, status):
        l = self.app.get_object_or_404(Layer, code=layer)
        LayerUserSettings.set_layer_visibility(request.user, l, status)
        return {"status": True}

    def get_add_menu(self):
        def get_menu_item(d):
            r = []
            for i in sorted(d):
                item = {"text": i}
                if isinstance(d[i], dict):
                    # Submenu
                    item["menu"] = get_menu_item(d[i])
                else:
                    # Item
                    item["objectTypeId"] = d[i]
                r += [item]
            return r

        d = {}
        # All models with geopoint interface
        for mt in ObjectModel.objects.filter(data__geopoint__layer__exists=True):
            parts = mt.name.split(" | ")
            m = d
            for p in parts[:-1]:
                if p not in m:
                    m[p] = {}
                m = m[p]
            m[parts[-1]] = str(mt.id)
        #
        return get_menu_item(d)

    def api_create(self, request, model=None, name=None,
                   srid=None, x=None, y=None):
        # Find suitable container
        to_pop = model.name == "Ducts | Cable Entry"
        p = (x, y, srid)
        if to_pop:
            # Cable entries are attached to nearest PoP
            pop_layers = list(Layer.objects.filter(code__startswith="pop_"))
            np, npd = map.find_nearest_d(p, pop_layers)
        else:
            # Or to the objects on same layer
            layer = Layer.objects.get(
                code=model.get_data("geopoint", "layer")
            )
            np, npd = map.find_nearest_d(p, layer)
        # Check nearest area
        layer = Layer.objects.get(code="areas")
        ap, apd = map.find_nearest_d(p, layer)
        if ap and (not np or apd < npd):
            np, npd = ap, apd
        # Check nearest city
        layer = Layer.objects.get(code="cities")
        ap, apd = map.find_nearest_d(p, layer)
        if ap and (not np or apd < npd):
            np, npd = ap, apd
        # Get best nearest container
        if to_pop and np.layer.code.startswith("pop_"):
            container = np.id
        else:
            container = np.container
        # Create object
        o = Object(
            name=name,
            model=model,
            container=container,
            data={
                "geopoint": {
                    "srid": srid,
                    "x": x,
                    "y": y
                }
            }
        )
        o.save()
        return {
            "id": str(o.id)
        }
