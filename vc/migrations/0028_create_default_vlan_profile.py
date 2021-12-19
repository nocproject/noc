# ----------------------------------------------------------------------
# Create default VLAN Profile and L2 Domain profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details

# Third-party modules
import bson

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash


class Migration(BaseMigration):
    def migrate(self):
        # Create default VLAN Profile
        vlan_prof_id = bson.ObjectId("61bee6a55c42c21338453612")
        self.mongo_db["vlanprofiles"].insert_one(
            {
                "_id": vlan_prof_id,
                "name": "default",
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(vlan_prof_id)),
            }
        )
        # Create default L2 Domain Profile
        l2domain_profile_id = bson.ObjectId("61bee6f45c42c21338453613")
        self.mongo_db["l2domainprofiles"].insert_one(
            {
                "_id": l2domain_profile_id,
                "name": "default",
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(l2domain_profile_id)),
                "vlan_discovery_policy": "E",
            }
        )
        # Create default L2 Domain
        l2dom_id = bson.ObjectId("61bee7425c42c21338453614")
        self.mongo_db["l2domains"].insert_one(
            {
                "_id": l2dom_id,
                "name": "default",
                "description": "Default L2 Domain Profile",
                "profile": l2domain_profile_id,
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(l2dom_id)),
            }
        )
