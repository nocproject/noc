# ----------------------------------------------------------------------
# Create default VLAN Profile and L2 Domain profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create default VLAN Profile
        self.mongo_db["vlanprofiles"].insert_one(
            {
                "_id": ObjectId("61bee6a55c42c21338453612"),
                "name": "default",
                "workflow": ObjectId("5a01d980b6f529000100d37a"),
                "labels": [],
                "effective_labels": [],
                "bi_id": 2881867143753311142,
            }
        )
        # Create default L2 Domain Profile
        self.mongo_db["l2domainprofiles"].insert_one(
            {
                "_id": ObjectId("61bee6f45c42c21338453613"),
                "name": "default",
                "workflow": ObjectId("5a01d980b6f529000100d37a"),
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": 1009096612210647130,
                "vlan_discovery_policy": "E",
            }
        )
        # Create default L2 Domain
        self.mongo_db["l2domains"].insert_one(
            {
                "_id": ObjectId("61bee7425c42c21338453614"),
                "name": "default",
                "description": "Default L2 Domain Profile",
                "profile": ObjectId("61bee6f45c42c21338453613"),
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": 2470941926019864228,
            }
        )
