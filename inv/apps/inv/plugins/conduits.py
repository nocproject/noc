# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv conduits plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.gis.measure import D
## NOC modules
from base import InvPlugin
from noc.gis.models.geodata import GeoData
from noc.inv.models.object import Object
from noc.lib.geo import distance, bearing, bearing_sym
from noc.gis.map import map
from noc.sa.interfaces.base import (DocumentParameter, FloatParameter,
                                    DictListParameter, IntParameter,
                                    BooleanParameter)


class ConduitsPlugin(InvPlugin):
    name = "conduits"
    js = "NOC.inv.inv.plugins.conduits.ConduitsPanel"

    MAX_CONDUIT_LENGTH = 1000
    SINGLE_CONNECTION_MODELS = set(["Ducts | Cable Entry"])

    def init_plugin(self):
        super(ConduitsPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_get_neighbors" % self.name,
            self.api_get_neighbors,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/get_neighbors/$" % self.name,
            method=["GET"]
        )
        self.add_view(
             "api_plugin_%s_create_conduits" % self.name,
             self.api_create_conduits,
             url="^(?P<id>[0-9a-f]{24})/plugin/%s/$" % self.name,
             method=["POST"],
             validate={
                 "conduits": DictListParameter(attrs={
                     "target": DocumentParameter(Object),
                     "project_distance": FloatParameter(),
                     "conduits": DictListParameter(attrs={
                         "n": IntParameter(),
                         "x": IntParameter(),
                         "y": IntParameter(),
                         "d": IntParameter(),
                         "status": BooleanParameter()
                     })
                 })
             }
        )

    def get_data(self, request, object):
        conduits = []
        try:
            gd = GeoData.objects.get(object=str(object.id))
        except GeoData.DoesNotExist:
            gd = None
        for c, remote, _ in object.get_genderless_connections("conduits"):
            map_distance = None
            br = None
            sbr = None
            if gd:
                try:
                    rgd = GeoData.objects.get(object=str(remote.id))
                    map_distance = distance(gd.data, rgd.data)
                    br = bearing(gd.data, rgd.data)
                    sbr = bearing_sym(gd.data, rgd.data)
                except GeoData.DoesNotExist:
                    pass
            conduits += [{
                "connection_id": str(c.id),
                "target_id": str(remote.id),
                "target_name": remote.name,
                "target_model_name": remote.model.name,
                "map_distance": map_distance,
                "project_distance": c.data.get("project_distance"),
                "n_conduits": len(c.data.get("conduits", [])),
                "conduits": c.data.get("conduits", []),
                "bearing": br,
                "s_bearing": sbr
            }]
        return {
            "id": str(object.id),
            "name": object.name,
            "conduits": conduits
        }

    def is_single_connection(self, o):
        return o.model.name in self.SINGLE_CONNECTION_MODELS

    def api_get_neighbors(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        try:
            og = GeoData.objects.get(object=str(o.id))
        except GeoData.DoesNotExist:
            return []
        layers = map.get_conduits_layers()
        connected = set(
            str(ro.id) for _, ro, _ in o.get_genderless_connections("conduits"))
        if self.is_single_connection(o) and connected:
            # Connection limits exceed
            return []
        r = []
        for g in GeoData.objects.filter(
                layer__in=layers,
                data__distance_lte=(
                    og.data, D(m=self.MAX_CONDUIT_LENGTH)
                )).exclude(object=id).distance(og.data).order_by("distance"):
            # Check object has no connection with this one
            if g.object in connected:
                continue
            ro = Object.objects.filter(id=g.object).first()
            if not ro:
                continue
            # Exclude already connected cable entries
            if (self.is_single_connection(ro) and
                    len(ro.get_genderless_connections("conduits"))):
                continue
            # Feed data
            d = distance(og.data, g.data)
            sbr = bearing_sym(og.data, g.data)
            r += [{
                "id": str(g.object),
                "label": "%s (%s, %dm)" % (ro.name, sbr, d),
                "s_bearing": sbr,
                "map_distance": d,
                "name": ro.name
            }]
        return r

    def api_create_conduits(self, request, id, conduits=None):
        o = self.app.get_object_or_404(Object, id=id)
        conns = {}  # target -> conneciton
        for c, t, _ in o.get_genderless_connections("conduits"):
            conns[t] = c
        left = set(conns)
        for cd in conduits:
            target = cd["target"]
            if target not in left:
                # New record
                print "NEW", cd
                o.connect_genderless("conduits", target, "conduits", {
                    "project_distance": cd["project_distance"],
                    "conduits": cd["conduits"]
                })
            else:
                c = conns[target]
                # Updated
                if (cd["project_distance"] != c.data.get("project_distance") or
                    cd["conduits"] != c.data.get("conduits")):
                    # Updated
                    c.data["project_distance"] = cd["project_distance"]
                    c.data["conduits"] = cd["conduits"]
                    c.save()
                left.remove(target)
        # Deleted
        for x in left:
            conns[x].delete()
        return {"status": True}
