# ----------------------------------------------------------------------
# Set reference to Ping Failed alarms
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid
from hashlib import sha512

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    PF_UUID = "ec26e28d-0b64-4738-8c07-5ee3daca16f4"

    def migrate(self):
        acls_coll = self.mongo_db["noc.alarmclasses"]
        pf_doc = acls_coll.find_one({"uuid": uuid.UUID(self.PF_UUID)}, {"_id": 1})
        if not pf_doc:
            return  # Clean installation, nothing to migrate
        alarm_coll = self.mongo_db["noc.alarms.active"]
        bulk = []
        for doc in alarm_coll.find({"alarm_class": pf_doc["_id"]}, {"_id": 1, "managed_object": 1}):
            bulk.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": {"reference": self.get_reference_hash(f"p:{doc['managed_object']}")}},
                )
            )
        if bulk:
            alarm_coll.bulk_write(bulk)

    @staticmethod
    def get_reference_hash(reference: str) -> bytes:
        return sha512(reference.encode("utf-8")).digest()[:10]
