# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv conduits plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## Django modules
from django.contrib.gis.measure import D
## NOC modules
from base import InvPlugin
from noc.gis.models.geodata import GeoData
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.lib.geo import distance, bearing, bearing_sym
from noc.gis.map import map
from noc.sa.interfaces.base import (DocumentParameter, FloatParameter,
                                    DictListParameter, IntParameter,
                                    BooleanParameter, ObjectIdParameter)


class ConduitsPlugin(InvPlugin):
    name = "conduits"
    js = "NOC.inv.inv.plugins.conduits.ConduitsPanel"

    MAX_CONDUIT_LENGTH = 1000
    SINGLE_CONNECTION_MODELS = set(["Ducts | Cable Entry"])
    CONDUITS_MODEL = "Ducts | Conduits"

    def init_plugin(self):
        super(ConduitsPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_get_neighbors" % self.name,
            self.api_get_neighbors,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/get_neighbors/$" % self.name,
            method=["GET"]
        )
        self.add_view(
             "api_plugin_%s_create_ducts" % self.name,
             self.api_create_ducts,
             url="^(?P<id>[0-9a-f]{24})/plugin/%s/$" % self.name,
             method=["POST"],
             validate={
                 "ducts": DictListParameter(attrs={
                     "target": DocumentParameter(Object),
                     "project_distance": FloatParameter(),
                     "conduits": DictListParameter(attrs={
                         "id": DocumentParameter(Object, required=False),
                         "n": IntParameter(),
                         "x": IntParameter(),
                         "y": IntParameter(),
                         "status": BooleanParameter()
                     })
                 })
             }
        )
        #
        self.conduits_model = ObjectModel.objects.get(name=self.CONDUITS_MODEL)

    def get_data(self, request, object):
        ducts = []
        # Get spatial object
        try:
            gd = GeoData.objects.get(object=str(object.id))
        except GeoData.DoesNotExist:
            gd = None
        # Get all conduits
        conduits = defaultdict(list)
        for c, remote, _ in object.get_genderless_connections("conduits"):
            conduit, _ = c.p2p_get_other(object)
            for cc, t, _ in conduit.get_genderless_connections("conduits"):
                if t != object:
                    conduits[t] += [{
                        "id": str(conduit.id),
                        "n": int(conduit.name),
                        "x": cc.data["plan"]["x"],
                        "y": cc.data["plan"]["y"],
                        "d": 100,  # remote.data.get("...."),
                        "status": True  # remote.data....
                    }]
        # Get neighbor ducts
        for c, remote, _ in object.get_genderless_connections("ducts"):
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
            cd = conduits[remote]
            ducts += [{
                "connection_id": str(c.id),
                "target_id": str(remote.id),
                "target_name": remote.name,
                "target_model_name": remote.model.name,
                "map_distance": map_distance,
                "project_distance": c.data.get("project_distance"),
                "n_conduits": len(cd),
                "conduits": cd,
                "bearing": br,
                "s_bearing": sbr
            }]
        return {
            "id": str(object.id),
            "name": object.name,
            "ducts": ducts
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
            str(ro.id) for _, ro, _ in o.get_genderless_connections("ducts"))
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
                    len(ro.get_genderless_connections("ducts"))):
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

    def api_create_ducts(self, request, id, ducts=None):
        o = self.app.get_object_or_404(Object, id=id)
        conns = {}  # target -> conneciton
        for c, t, _ in o.get_genderless_connections("ducts"):
            conns[t] = c
        conduits = defaultdict(list)  # target, conduits
        for c, t, _ in o.get_genderless_connections("conduits"):
            for cc, tt, _ in t.get_genderless_connections("conduits"):
                if tt.id != o.id:
                    conduits[tt] += [t]
        left = set(conns)
        for cd in ducts:
            target = cd["target"]
            if target not in left:
                # New record
                o.connect_genderless(
                    "ducts", target, "ducts",
                    data={
                        "project_distance": cd["project_distance"]
                    },
                    type="ducts"
                )
            else:
                c = conns[target]
                # Updated
                if cd["project_distance"] != c.data.get("project_distance"):
                    # Updated
                    c.data["project_distance"] = cd["project_distance"]
                    c.type = "ducts"
                    c.save()
                left.remove(target)
            left_conduits = set(conduits[target])
            for cc in cd["conduits"]:
                if "id" not in cc or cc["id"] not in left_conduits:
                    # Create new conduit
                    conduit = Object(
                        name=str(cc["n"]),
                        model=self.conduits_model
                    )
                    conduit.save()
                    # Connect to both manholes
                    o.connect_genderless(
                        "conduits", conduit, "conduits",
                        data={
                            # Conduit position
                            "plan": {
                                "x": cc["x"],
                                "y": cc["y"]
                            }
                        },
                        type="conduits"
                    )
                    target.connect_genderless(
                        "conduits", conduit, "conduits",
                        data={
                            # @todo: Mirror position
                            # Conduit position
                            "plan": {
                                "x": cc["x"],
                                "y": cc["y"]
                            }
                        },
                        type="conduits"
                    )
                else:
                    # Change.
                    conduit = cc["id"]
                    for ccc, ro, _ in conduit.get_genderless_connections("conduits"):
                        odata = ccc.data.copy()
                        ccc.data["plan"]["x"] = cc["x"]
                        ccc.data["plan"]["y"] = cc["y"]
                        if ccc.data != odata:
                            ccc.save()
                if "id" in cc:
                    left_conduits.remove(cc["id"])
            for t in left_conduits:
                cc = left_conduits[t]
                print "DEL", cc
        # Deleted
        for x in left:
            for c, remote, _ in conns[x].get_genderless_connecitons("conduits"):
                remote.delete()
            conns[x].delete()
        return {"status": True}
