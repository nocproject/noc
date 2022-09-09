# ----------------------------------------------------------------------
# Create default VLAN Profile and L2 Domain profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details

# Third-pary modules
from bson import ObjectId, int64

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create default VLAN Profile
        self.mongo_db["vlanprofiles"].update_one(
            {"name": "default"},
            {
                "$set": {
                    # "_id": ObjectId("61bffba63adaa22083f2abfc"),
                    "name": "default",
                    "description": "Default VLAN Profile",
                    "workflow": ObjectId("5a01d980b6f529000100d37a"),
                    "labels": [],
                    "effective_labels": [],
                    "bi_id": int64.Int64(7743152101335604792),
                }
            },
            upsert=True,
        )
        # Create default L2 Domain Profile
        self.mongo_db["l2domainprofiles"].update_one(
            {"name": "default"},
            {
                "$set": {
                    # "_id": ObjectId("61bee6f45c42c21338453613"),
                    "name": "default",
                    "description": "Default L2Domain Profile",
                    "workflow": ObjectId("5a01d980b6f529000100d37a"),
                    "pools": [],
                    "labels": [],
                    "effective_labels": [],
                    "bi_id": int64.Int64(1009096612210647130),
                    "vlan_discovery_policy": "E",
                }
            },
            upsert=True,
        )
        # Create default L2 Domain
        l2domain_profile_id = self.mongo_db["l2domainprofiles"].find_one(
            {"name": "default"}, {"_id": 1}
        )["_id"]
        self.mongo_db["l2domains"].insert_one(
            {
                "_id": ObjectId("61bee7425c42c21338453614"),
                "name": "default",
                "description": "Default L2 Domain",
                "profile": l2domain_profile_id,
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": int64.Int64(2470941926019864228),
            }
        )
