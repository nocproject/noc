# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Link's dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

import string
# NOC modules
from base import BaseDashboard
from noc.inv.models.link import Link


class LinkDashboard(BaseDashboard):
    name = "link"

    def resolve_object(self, object):
        try:
            return Link.objects.get(id=object)
        except Link.DoesNotExist:
            raise self.NotFound()

    def render(self):
        mos = self.object.managed_objects
        ifaces = self.object.interfaces
        self.logger.info("Link ID is: %s, MO: %s, Ifaces: %s" % (self.object.id, mos, ifaces))
        list = []
        refId = string.lowercase[:14]
        fish = {
            "current": {},
            "datasource": None,
            "hide": 2,
            "includeAll": False,
            "multi": False,
            "name": "device_a",
            "options": [],
            "query": "",
            "refresh": 0,
            "type": "custom"
            }
        for o in mos:
            v = {
                "text": o.name,
                "value": o.name
            }

            c = {
                "name": "device_%s" % refId[mos.index(o)],
                "query": o.name,
                "options": v,
                "current": v
            }
            fish.update(c)
            list += [fish.copy()]

        query = ",".join([i.name for i in ifaces])
        options = [{"text": i.name, "value": i.name} for i in ifaces]
        for i in ifaces:
            v = {
                "text": i.name,
                "value": i.name
            }

            c = {
                "name": "interface_%s" % refId[ifaces.index(i)],
                "label": u"Интерфейс %s" % refId[ifaces.index(i)].upper(),
                "query": query,
                "options": options,
                "current": v
            }
            fish.update(c)
            list += [fish.copy()]

        config = [{"template": "link_dashboard", "templating": {"list": list}}]
        r = self.generator(config)
        return r

    def generator(self, config):
        """Create dashboard from config and template"""
        t = self.templates
        r = []
        for c in config:
            # templ_name = c["template"]
            templ_name = c.pop("template")
            # r1 = t[c["template"]]
            if "panel" in templ_name:
                m2 = []
                for tg in c.pop("targets"):
                    t[tg.pop("template")].update(tg)
                    m2.append(t["panel.targets_basic"].copy())

                c["targets"] = m2[:]
                # t[templ_name]["targets"] = t["targets"].update(c.pop("targets"))
                t[templ_name].update(c)
                r["rows"][-1]["panels"] += [t[templ_name].copy()]
            elif "row" in templ_name:
                t[templ_name].update(c)
                r["rows"] += [t[templ_name].copy()]
            elif "dashboard" in templ_name or "." not in templ_name:
                t[templ_name].update(c)
                r = t[templ_name].copy()
            else:
                t[templ_name].update(c)
                r += [t[templ_name].copy()]
        return r
