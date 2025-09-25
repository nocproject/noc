# ----------------------------------------------------------------------
# Migrate Active Alarm discriminator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib

from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.comp import smart_bytes


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        ac_map = {}
        for ac in db["noc.alarmclasses"].find({}, {"name": 1}):
            ac_map[ac["_id"]] = ac["name"]

        bulk = []
        active_alarms = db.noc.alarms.active
        # archived_alarms = db.noc.alarms.archive
        active_alarms.find({"vars": {}})
        for ac in (active_alarms,):
            for doc in ac.aggregate(
                [
                    {"$match": {"vars": {}}},
                    {"$group": {"_id": "$alarm_class", "summary": {"$sum": 1}}},
                ]
            ):
                if doc["_id"] not in ac_map:
                    continue
                d_hash = self.get_hash(ac_map[doc["_id"]])
                bulk += [
                    UpdateMany(
                        {"alarm_class": doc["_id"], "vars": {}}, {"$set": {"discriminator": d_hash}}
                    )
                ]
            if bulk:
                ac.bulk_write(bulk)

    @staticmethod
    def get_hash(name):
        return hashlib.sha1(smart_bytes(name)).hexdigest()
