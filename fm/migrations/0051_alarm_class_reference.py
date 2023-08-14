# ----------------------------------------------------------------------
# Migrate Active Alarm reference
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib

# Third-party modules
from pymongo import UpdateOne, UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):

        db = self.mongo_db
        ac_map = {}
        processed = set()
        ac_bulk = []
        for ac in db["noc.alarmclasses"].find({}, {"name": 1, "discriminator": 1}):
            ac_map[ac["_id"]] = ac.get("discriminator", [])
            if "discriminator" in ac and tuple(ac["discriminator"]) not in processed:
                ac_bulk += [
                    UpdateMany(
                        {"discriminator": ac["discriminator"]},
                        {"$set": {"reference": ac["discriminator"]}},
                    )
                ]
                processed.add(tuple(ac["discriminator"]))

        bulk = []
        active_alarms = db.noc.alarms.active
        # archived_alarms = db.noc.alarms.archive
        active_alarms.find({"vars": {}})
        for aa in (active_alarms,):
            for doc in aa.find(
                {"managed_object": {"$exists": True}, "alarm_class": {"$exists": True}},
                {"vars.message": 0},
            ):
                if doc["alarm_class"] not in ac_map:
                    continue
                reference = self.get_default_reference(
                    doc["managed_object"],
                    doc["alarm_class"],
                    doc["vars"],
                    ac_map.get(doc["alarm_class"], []),
                )
                r_hash = self.get_reference_hash(reference)
                bulk += [UpdateOne({"_id": doc["_id"]}, {"$set": {"reference": r_hash}})]
                if len(bulk) > 500:
                    aa.bulk_write(bulk)
                    bulk = []
        if bulk:
            aa.bulk_write(bulk)
        active_alarms.update_many({}, {"$unset": {"discriminator": 1}})
        if ac_bulk:
            db["noc.alarmclasses"].bulk_write(ac_bulk)
        db["noc.alarmclasses"].update_many({}, {"$unset": {"discriminator": 1}})

    @staticmethod
    def get_reference_hash(reference: str) -> bytes:
        """
        Generate hashed form of reference
        """
        return hashlib.sha512(reference.encode("utf-8")).digest()[:10]

    @staticmethod
    def get_default_reference(managed_object, alarm_class, vars, refs) -> str:
        """"""
        if not vars:
            return f"e:{managed_object}:{alarm_class}"
        var_suffix = ":".join(
            str(vars.get(n, "")).replace("\\", "\\\\").replace(":", r"\:") for n in refs
        )
        return f"e:{managed_object}:{alarm_class}:{var_suffix}"
