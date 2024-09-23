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
        for o_id, rid in self.db.execute(
            "SELECT id, remote_id FROM sa_managedobject where remote_id != ''"
        ):
            mos_rid[o_id] = rid
        iface_svc = {}  # service -> iface map
        for iface in mdb["noc.interfaces"].find(
            {"service": {"$exists": True}}, {"_id": 1, "service": 1}
        ):
            iface_svc[iface["service"]] = f"if:{iface['_id']}"
        siface_svc = {}
        for si in mdb["noc.subinterfaces"].find(
            {"service": {"$exists": True}}, {"_id": 1, "service": 1}
        ):
            siface_svc[si["service"]] = f"si:{si['_id']}"
        for svc in self.mongo_db["noc.services"].find(
            {"nri_port": {"$exists": True}, "managed_object": {"$exists": True}}
        ):
            if svc["managed_object"] not in mos_rid:
                continue
            sid = svc["_id"]
            si = {
                "service": sid,
                "managed_object": svc["managed_object"],
                "nri_port": svc["nri_port"],
                "port": 0,
                "addresses": [],
                "sources": ["etl", "discovery"],
                "remote_id": mos_rid[svc["managed_object"]],
                "resources": [],
            }
            if sid in iface_svc:
                si["resources"].append(iface_svc[sid])
            if sid in siface_svc:
                si["resources"].append(siface_svc[sid])
            bulk.append(InsertOne(si))
            if len(bulk) > BULK:
                si_db.bulk_write(bulk)
                bulk = []
        if bulk:
            si_db.bulk_write(bulk)
