# ---------------------------------------------------------------------
# inv.inv crossing plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from itertools import chain

# NOC modules
from .base import InvPlugin
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.objectconnection import ObjectConnection


class CrossingPlugin(InvPlugin):
    name = "crossing"
    js = "NOC.inv.inv.plugins.crossing.CrossingPanel"

    def get_data(self, request, o):
        cables_model = ObjectModel.objects.filter(
            data__match={"interface": "length", "attr": "length", "value__gte": 0},
        )
        oc_ids = chain.from_iterable(
            ObjectConnection.objects.filter(
                __raw__={"connection": {"$elemMatch": {"object": {"$in": o.get_nested_ids()}}}}
            ).scalar("connection")
        )

        r = []
        for oo in Object.objects.filter(
            model__in=cables_model, id__in=[x.object.id for x in oc_ids]
        ):
            c1, c2 = None, None
            c = ObjectConnection.objects.filter(
                __raw__={"connection": {"$elemMatch": {"object": oo.id}}}
            )[:2]
            if c:
                c1 = [c for c in c[0].connection if c.object != oo][0]
            if len(c) > 1:
                c2 = [c for c in c[1].connection if c.object != oo][0]
            r += [
                {
                    "name": oo.name,
                    "id": str(oo.id),
                    "length": oo.get_data("length", "length"),
                    "model": str(oo.model.id),
                    "model__label": oo.model.name,
                    "object_start": str(c1.object.id),
                    "object_start_slot": c1.name,
                    "object_start__label": c1.object.name if c1 else "",
                    "object_end": str(c2.object.id),
                    "object_end_slot": c2.name,
                    "object_end__label": c2.object.name if c2 else "",
                }
            ]
        return r
