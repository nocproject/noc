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
from noc.bi.models.managedobjects import ManagedObject as ManagedObjectBI
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
    is_snapshot = True

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
        self.mo_stream = Stream(ManagedObjectBI, prefix)

    def extract(self):
        nr = 0
        ts = datetime.datetime.now()
        # External data
        x_data = [
            self.get_interfaces(),
            self.get_links(),
            self.get_caps()
        ]
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
                "pool": mo.pool,
                # "object_profile": mo.object_profile,
                "vendor": mo.vendor,
                "platform": mo.platform,
                "version": mo.version,
                "name": mo.name,
                "address": mo.address,
                "is_managed": mo.is_managed,
                # subscribers
                # services
            }
            # Apply external data
            for data in x_data:
                d = data.get(mo.id)
                if d:
                    r.update(d)
            # Submit
            self.mo_stream.push(**r)
            nr += 1
        self.mo_stream.finish()
        return nr

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
        return dict((o, {
            "n_neighbors": neighbors[o],
            "n_links": t[o],
            "nri_links": r[o, "nri"],
            "mac_links": r[o, "mac"],
            "stp_links": r[o, "stp"],
            "lldp_links": r[o, "lldp"],
            "cdp_links": r[o, "cdp"]
        }) for o in t)

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
        return dict((d["_id"], {
            "n_interfaces": d["total"]
        }) for d in r)

    def get_caps(self):
        # name -> id map
        caps = dict(
            (self.CAPS_MAP[d["name"]], d["_id"])
            for d in Capability._get_collection().find({
                "name": {
                    "$in": list(self.CAPS_MAP)
                }
            }, {
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
