# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.map application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.inv.models.networkchart import NetworkChart
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link


class MapAppplication(ExtApplication):
    """
    inv.net application
    """
    title = "Network Map"
    menu = "Network Map"
    icon = "icon_map"

    @view(url="^chart/(?P<chart_id>\d+)/$", method=["GET"],
        access="launch")
    def chart(self, request, chart_id):
        chart = self.get_object_or_404(NetworkChart, id=int(chart_id))
        w = 30
        h = 30
        s = 20
        r = []
        # Get managed objects
        mos = list(chart.selector.managed_objects)
        mo_ids = [o.id for o in mos]
        # Get links
        if_ids = set(i.id for i in
                  Interface.objects.filter(managed_object__in=mo_ids,
                      type__in=["physical", "management"]))
        links = []
        mo_links = defaultdict(list)  # mo -> [links]
        linked_ports = defaultdict(list)  # link -> [port1, port2]
        for link in Link.objects.filter(interfaces__in=if_ids):
            interfaces = link.interfaces
            if not [i for i in interfaces if i.id not in if_ids]:
                # Both ends on chart
                links += [link]
                for i in interfaces:
                    if i.managed_object not in links:
                        mo_links[i.managed_object] += [link]
        # Attach nodes
        x = 10
        y = h
        for mo in mos:
            # Managed Objects
            n = {
                "type": "node",
                "id": mo.id,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "label": mo.name,
                "label_position": "s",
                "shape": "xor",
                "ports": []
            }
            # Used ports
            for link in mo_links[mo]:
                interfaces = [i for i in link.interfaces if i.managed_object == mo]
                p_id = "%d:%s" % (mo.id, link.id)
                if p_id not in linked_ports[link]:
                    n["ports"] += [{
                        "id": p_id,
                        "label": ", ".join(i.name for i in interfaces)
                    }]
                    linked_ports[link] += [p_id]
            #
            r += [n]
            x += w + s
            y += h + s
        # Attach links
        for link in linked_ports:
            lp = linked_ports[link]
            if len(lp) == 2:
                r += [{
                    "type": "link",
                    "id": str(link.id),
                    "ports": lp
                }]
        return r
