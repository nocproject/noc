# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
# NOC modules
from base import BaseExtractor
from noc.sa.models.managedobject import ManagedObject
from noc.core.etl.bi.stream import Stream
from noc.config import config
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.capability import Capability
from noc.sa.models.objectcapabilities import ObjectCapabilities


class ManagedObjectsExtractor(BaseExtractor):
    name = "managedobjects"
    extract_delay = config.bi.extract_delay_alarms
    clean_delay = config.bi.clean_delay_alarms
    reboot_interval = datetime.timedelta(
        seconds=config.bi.reboot_interval)

    # Caps to field mapping
    CAPS_MAP = {
        "Network | STP": "has_stp",
        "Network | CDP": "has_cdp",
        "Network | LLDP": "has_lldp",
        "SNMP": "has_snmp",
        "SNMP | v1": "has_snmp_v1",
        "SNMP | v2c": "has_snmp_v2c",
    }

    def __init__(self, prefix, start, stop):
        super(ManagedObjectsExtractor, self).__init__(prefix, start,
                                                      stop)
        self.stream = Stream(ManagedObject, prefix)

    def extract(self):
        ts = datetime.datetime.now()
        # Extract links
        link_totals, link_methods, neighbors = self.get_links()
        # Extract caps
        caps = self.get_caps()
        # Extract interfaces
        interfaces = self.get_interfaces()
        # Extract managed objects
        for mo in ManagedObject.objects.all():
            r = {
                "ts": ts,
                "managed_object": mo,
                "profile": mo.profile,
                "administrative_domain": mo.administrative_domain,
                "segment": mo.segment,
                "container": mo.container,
                "level": mo.object_profile.level,
                "x": mo.x,
                "y": mo.y,
                # "object_profile": mo.object_profile,
                "vendor": mo.vendor,
                "platform": mo.platform,
                "version": mo.version,
                "name": mo.name,
                "address": mo.address,
                "is_managed": mo.is_managed,
                # Topology
                "n_neighbors": neighbors[mo.id],
                "n_links": link_totals[mo.id],
                "nri_links": link_methods[mo.id, "nri"],
                "mac_links": link_methods[mo.id, "mac"],
                "stp_links": link_methods[mo.id, "stp"],
                "lldp_links": link_methods[mo.id, "lldp"],
                "cdp_links": link_methods[mo.id, "cdp"],
                #
                "n_interfaces": interfaces.get(mo.id, 0),
                # subscribers
                # services
            }
            # Update capabilities
            ocaps = caps.get(mo.id) or {}
            if ocaps:
                r.update(ocaps)
            self.stream.push(r)

    def get_links(self):
        """
        Build discovery method summary
        :return:
        """
        t = defaultdict(int)  # object -> count
        r = defaultdict(int)  # object_id, method -> count
        neighbors = defaultdict(set)  # object_id -> {objects}
        for d in Link._get_collection().find():
            method = d.get("discovery_method")
            linked = d.get("linked_objects", [])
            for o in linked:
                r[o, method] += 1
                t[o] += 1
                neighbors[o].update(linked)
        n = dict((o, len(neighbors[o]) - 1) for o in neighbors)
        return t, r, n

    def get_interfaces(self):
        """
        Build interface counts
        :return:
        """
        r = Interface._get_collection().aggregate([
            {
                "$match": {
                    "type": "physical"
                }
            },
            {
                "$group": {
                    "_id": "$managed_object",
                    "total": {
                        "$sum": 1
                    }
                }
            }
        ])
        return dict((d["_id"], d["total"]) for d in r)

    def get_caps(self):
        # name -> id map
        caps = dict(
            (self.CAPS_MAP[d["name"]], d["_id"])
            for d in Capability._get_collection().find({
                "name": {
                    "$in": list(self.CAPS_MAP)
                }
            },
                {
                    "_id": 1,
                    "name": 1
                })
        )
        # object -> caps
        add_expr = dict(
            (c, {"$in": [caps[c], "$caps.capability"]})
            for c in caps
        )
        project_expr = dict((c, 1) for c in caps)
        project_expr["_id"] = 1
        return dict(
            (d["_id"], dict((x, d[x]) for x in d if x != "_id"))
            for d in ObjectCapabilities._get_collection().aggregate([
                {"$addFields": add_expr},
                {"$project": project_expr}
            ])
        )
