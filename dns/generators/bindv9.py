# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BINDv9 Zone Generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import noc.dns.generators
import time, os
from noc.dns.utils.zonefile import ZoneFile


class Generator(noc.dns.generators.Generator):
    name = "BINDv9"

    def get_zone(self, zone):
        return ZoneFile(
            zone=zone.name,
            records=zone.get_records()
        ).get_text()

    def get_include(self, ns):
        def ns_list(ds):
            s = [ns.ip for ns in ds.order_by("name") if ns.ip]
            if s:
                return "; ".join(s) + ";"
            else:
                return None

        s = """#
# WARNING: This is auto-generated file
# Do not edit manually
#
"""
        if ns.autozones_path:
            autozones_path = ns.expand_vars(ns.autozones_path)
        else:
            autozones_path = "autozones"
            # id -> (zone, is_master, masters, slaves)
        zones = {}
        for p in ns.masters.all():
            masters = ns_list(p.masters)
            slaves = ns_list(p.slaves)
            for z in p.dnszone_set.filter(is_auto_generated=True):
                zones[z.id] = (z.name, True, masters, slaves)
        for p in ns.slaves.all():
            masters = ns_list(p.masters)
            slaves = ns_list(p.slaves)
            for z in p.dnszone_set.filter(is_auto_generated=True):
                zones[z.id] = (z.name, False, masters, slaves)
        zones = zones.values()
        zones.sort(lambda x, y: cmp(x[0], y[0]))
        for zone, is_master, masters, slaves in zones:
            s += "zone %s {\n" % zone
            if is_master:
                s += "    type master;\n"
                s += "    file \"%s\";\n" % os.path.join(autozones_path, zone)
                if slaves:
                    s += "    allow-transfer {%s};\n" % slaves
            else:
                s += "    type slave;\n"
                s += "    file \"%s\";\n" % os.path.join(autozones_path, "slave", zone)
                if masters:
                    s += "    masters {%s};\n" % masters
            s += "};\n"
        s += """#
# End of auto-generated file
#
"""
        return s
