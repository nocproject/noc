# ---------------------------------------------------------------------
# inv.inv map plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.gis.map import map
from noc.gis.models.layer import Layer
from noc.gis.models.layerusersettings import LayerUserSettings
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object, ObjectAttr
from noc.sa.interfaces.base import (
    StringParameter,
    FloatParameter,
    BooleanParameter,
    DocumentParameter,
    UnicodeParameter,
)
from .base import InvPlugin


class MapPlugin(InvPlugin):
    name = "map"
    js = "NOC.inv.inv.plugins.map.MapPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_get_layer" % self.name,
            self.api_get_layer,
            url=r"^plugin/%s/layers/(?P<layer>\S+)/$" % self.name,
            method=["GET"],
        )
        self.add_view(
            "api_plugin_%s_object_data" % self.name,
            self.api_object_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/object_data/$" % self.name,
            method=["GET"],
        )
        self.add_view(
            "api_plugin_%s_set_geopoint" % self.name,
            self.api_set_geopoint,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/set_geopoint/$" % self.name,
            method=["POST"],
            validate={"srid": StringParameter(), "x": FloatParameter(), "y": FloatParameter()},
        )
        self.add_view(
            "api_plugin_%s_set_layer_visibility" % self.name,
            self.api_set_layer_visibility,
            url="^plugin/%s/layer_visibility/$" % self.name,
            method=["POST"],
            validate={"layer": StringParameter(), "status": BooleanParameter()},
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
                "y": FloatParameter(),
            },
        )

    def get_parent(self, o):
        """
        Find parent object with geopoint
        """
        p = o.parent
        while p:
            if p.is_point:
                return p
            p = p.parent

    def get_data(self, request, o):
        layers = [
            {
                "name": layer.name,
                "code": layer.code,
                "min_zoom": layer.min_zoom,
                "max_zoom": layer.max_zoom,
                "stroke_color": "#%06x" % layer.stroke_color,
                "fill_color": "#%06x" % layer.fill_color,
                "stroke_width": layer.stroke_width,
                "point_radius": layer.point_radius,
                "show_labels": layer.show_labels,
                "stroke_dashstyle": layer.stroke_dashstyle,
                "point_graphic": layer.point_graphic,
                "is_visible": LayerUserSettings.is_visible_by_user(request.user, layer),
            }
            for layer in Layer.objects.order_by("zindex")
        ]
        srid, x, y = o.get_data_tuple("geopoint", ("srid", "x", "y"))
        if x is None or y is None or not srid:
            p = self.get_parent(o)
            if p:
                srid, x, y = p.get_data_tuple("geopoint", ("srid", "x", "y"))
        # @todo: Coordinates transform
        # Feed result
        return {
            "id": str(o.id),
            "zoom": map.get_default_zoom(o.get_data("geopoint", "layer"), object=o),
            "x": x if x is not None else config.web.map_lon,
            "y": y if y is not None else config.web.map_lat,
            "layer": o.get_data("geopoint", "layer"),
            "layers": layers,
            "add_menu": self.get_add_menu(),
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
        mos = {}
        o = self.app.get_object_or_404(Object, id=id)
        for mo in ManagedObject.objects.filter(container=id)[:10]:
            mos[mo.id] = {"moname": mo.name}
        return {"id": str(o.id), "name": o.get_address_text(), "model": o.model.name, "moname": mos}

    def get_conduits_layer(self, layer, x0, y0, x1, y1, srid):
        line = Layer.get_by_code("conduits")
        return map.get_connection_layer(line, x0, y0, x1, y1, srid)

    def get_pop_links_layer(self, layer, x0, y0, x1, y1, srid):
        line = Layer.get_by_code(layer)
        return map.get_connection_layer(line, x0, y0, x1, y1, srid)

    def api_set_layer_visibility(self, request, layer, status):
        line = self.app.get_object_or_404(Layer, code=layer)
        LayerUserSettings.set_layer_visibility(request.user, line, status)
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
        for mt in ObjectModel.objects.filter(
            data__match={"interface": "geopoint", "attr": "layer"}
        ):
            parts = mt.name.split(" | ")
            m = d
            for p in parts[:-1]:
                if p not in m:
                    m[p] = {}
                m = m[p]
            m[parts[-1]] = str(mt.id)
        #
        return get_menu_item(d)

    def api_create(self, request, model=None, name=None, srid=None, x=None, y=None):
        # Find suitable container
        to_pop = model.name == "Ducts | Cable Entry"
        p = (x, y, srid)
        if to_pop:
            # Cable entries are attached to nearest PoP
            pop_layers = list(Layer.objects.filter(code__startswith="pop_"))
            np, npd = map.find_nearest_d(p, pop_layers)
        else:
            # Or to the objects on same layer
            layer = Layer.objects.get(code=model.get_data("geopoint", "layer"))
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
            parent = np.id
        else:
            parent = np.parent
        # Create object
        o = Object(
            name=name,
            model=model,
            parent=parent,
            data=[
                ObjectAttr(scope="", interface="geopoint", attr="srid", value=srid),
                ObjectAttr(scope="", interface="geopoint", attr="x", value=x),
                ObjectAttr(scope="", interface="geopoint", attr="y", value=y),
            ],
        )
        o.save()
        return {"id": str(o.id)}
