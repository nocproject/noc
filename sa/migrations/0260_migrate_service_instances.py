# ---------------------------------------------------------------------
# Migrate Service nri to Service Instances
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-pary modules
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration

BULK = 5000


class Migration(BaseMigration):
    def migrate(self):
        mdb = self.mongo_db
        si_db = mdb["serviceinstances"]
        bulk = []
        mos_rid = {}
        for o_id, rid in self.db.execute("SELECT id, remote_id FROM sa_managedobject"):
            mos_rid[o_id] = rid or None
        iface_svc = {}  # service -> iface map
        for iface in mdb["noc.interfaces"].find(
            {"service": {"$exists": True}}, {"_id": 1, "managed_object": 1, "service": 1}
        ):
            iface_svc[iface["service"]] = (f"if:{iface['_id']}", iface["managed_object"])
        siface_svc = {}
        for si in mdb["noc.subinterfaces"].find(
            {"service": {"$exists": True}}, {"_id": 1, "managed_object": 1, "service": 1}
        ):
            siface_svc[si["service"]] = (f"si:{si['_id']}", si["managed_object"])
        for svc in self.mongo_db["noc.services"].find():
            sid = svc["_id"]
            si = {
                "type": "network",
                "service": sid,
                "port": 0,
                "addresses": [],
                "sources": ["discovery"],
                "resources": [],
            }
            if svc.get("managed_object") in mos_rid:
                si["managed_object"] = svc["managed_object"]
                if mos_rid[svc["managed_object"]]:
                    si["remote_id"] = mos_rid[svc["managed_object"]]
            if sid in iface_svc:
                si["resources"].append(iface_svc[sid][0])
                si["managed_object"] = iface_svc[sid][1]
            if sid in siface_svc:
                si["resources"].append(siface_svc[sid][0])
                si["managed_object"] = siface_svc[sid][1]
            if "managed_object" not in si:
                continue
            if svc.get("nri_port"):
                si["nri_port"] = svc["nri_port"]
                si["sources"].append("etl")
            bulk.append(InsertOne(si))
            if len(bulk) > BULK:
                si_db.bulk_write(bulk)
                bulk = []
        if bulk:
            si_db.bulk_write(bulk)
        self.mongo_db["noc.interfaces"].update_many({}, {"$unset": {"service": 1}})
        self.mongo_db["noc.subinterfaces"].update_many({}, {"$unset": {"service": 1}})
