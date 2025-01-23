# ----------------------------------------------------------------------
# Event Classification Rule separate patterns to Profile and Source
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration

MONGO_CHUNK = 200


class Migration(BaseMigration):

    @staticmethod
    def get_patterns(patterns):
        r, source, profile, message_rx = [], None, None, None
        for p in patterns or []:
            key = p["key_re"].strip("^$")
            if key == "profile":
                profile = p["value_re"].strip("^$").replace("\\", "")
            elif key == "source":
                source = p["value_re"].strip("^$")
            elif key == "message":
                message_rx = p["value_re"]
            else:
                r.append(p)
        return r, source, profile, message_rx

    def migrate(self):
        # Update mongodb collections
        profile_map = {}
        for p in self.mongo_db["noc.profiles"].find():
            profile_map[p["name"]] = p["_id"]
        sources = {"syslog", "SNMP Trap", "system", "internal", "winevent", "other"}
        coll = self.mongo_db["noc.eventclassificationrules"]
        bulk = []
        for d in coll.find():
            p, source, profile, message_rx = self.get_patterns(d.get("patterns"))
            if not source or source not in sources:
                source = ["other"]
            else:
                source = [source]
            if profile and profile in profile_map:
                profile = [profile_map[profile]]
            else:
                profile = []
            ss = {"patterns": p, "sources": source, "profiles": profile}
            if message_rx:
                ss["message_rx"] = message_rx
            bulk.append(UpdateOne({"_id": d["_id"]}, {"$set": ss}))
            if len(bulk) >= MONGO_CHUNK:
                coll.bulk_write(bulk)
                bulk = []
        if bulk:
            coll.bulk_write(bulk)
