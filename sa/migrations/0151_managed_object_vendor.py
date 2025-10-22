# ----------------------------------------------------------------------
# Vendor attributes to collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import uuid

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField

OLD_VENDOR_MAP = {
    "Alcatel-Lucent": "ALU",
    "Alcatel": "ALU",
    "Arista Networks": "ARISTA",
    "Edge-Core": "EDGECORE",
    "Cisco Networks": "CISCO",
    "D-Link": "DLINK",
    "Extreme Networks": "EXTREME",
    "Extreme": "EXTREME",
    "f5 Networks": "F5",
    "Force10 Networks": "FORCE10",
    "Huawei Technologies Co.": "HUAWEI",
    "HP": "HP",
    "Juniper Networks": "JUNIPER",
    "NOC": "NOC",
    "NoName": "NONAME",
    "ZTE": "ZTE",
    "ZyXEL": "ZYXEL",
}

DUPLICATE_VENDOR_MAP = {"EXTREME NETWORKS": "Extreme", "ALCATEL": "ALU"}


class Migration(BaseMigration):
    def migrate(self):
        #
        # Vendor
        #

        # Select vendors
        vendors = {
            r[0]
            for r in self.db.execute(
                "SELECT DISTINCT value FROM sa_managedobjectattribute WHERE key = 'vendor'"
            )
        }
        pcoll = self.mongo_db["noc.vendors"]
        # Update inventory vendors records
        inventory_vendors = {}
        for v in pcoll.find():
            if v.get("code"):
                inventory_vendors[v["code"][0] if isinstance(v["code"], list) else v["code"]] = v[
                    "_id"
                ]
                continue
            if v["name"] in OLD_VENDOR_MAP:
                vc = OLD_VENDOR_MAP[v["name"]]
            else:
                vc = v["name"].split(" ")[0]
            vc = vc.upper()
            inventory_vendors[vc] = v["_id"]
            u = uuid.uuid4()
            pcoll.update_one({"_id": v["_id"]}, {"$set": {"code": vc, "uuid": u}})
        # Create vendors records
        for v in vendors:
            u = uuid.uuid4()
            vc = v.upper()
            if vc in inventory_vendors or vc in DUPLICATE_VENDOR_MAP:
                continue
            pcoll.update_one(
                {"code": vc},
                {"$set": {"code": vc}, "$setOnInsert": {"name": v, "uuid": u}},
                upsert=True,
            )
        # Get vendor record mappings
        vmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "code": 1}):
            vmap[d["code"]] = str(d["_id"])
        # Create .vendor field
        self.db.add_column(
            "sa_managedobject",
            "vendor",
            DocumentReferenceField("inv.Vendor", null=True, blank=True),
        )
        # Migrate profile data
        for v in vendors:
            if v.upper() in DUPLICATE_VENDOR_MAP:
                v = DUPLICATE_VENDOR_MAP[v.upper()]
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET vendor = %s
                WHERE
                  id IN (
                    SELECT managed_object_id
                    FROM sa_managedobjectattribute
                    WHERE
                      key = 'vendor'
                      AND value = %s
                  )
            """,
                [vmap[v.upper()], v],
            )
