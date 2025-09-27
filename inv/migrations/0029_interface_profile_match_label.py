# ----------------------------------------------------------------------
# Add InterfaceProfile match label to interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
from pymongo import UpdateMany, InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("inv", "0021_labels")]

    def migrate(self):
        bulk = []
        labels = []
        labels_bulk = [
            InsertOne(
                {
                    "_id": bson.ObjectId(),
                    "name": "noc::interface_profile::*",
                    "description": "Match Label for InterfaceProfile",
                    "bg_color1": 15105570,
                    "bg_color2": 15965202,
                    "is_protected": False,
                    "propagate": True,
                }
            )
        ]
        for ip in self.mongo_db["noc.interface_profiles"].find({}, {"_id": 1, "name": 1}):
            labels.append(f"noc::interface_profile::{ip['name']}::=")
            bulk += [
                UpdateMany(
                    {"profile": ip["_id"]},
                    {"$addToSet": {"effective_labels": f"noc::interface_profile::{ip['name']}::="}},
                )
            ]
        for ll in labels:
            labels_bulk += [
                InsertOne(
                    {
                        "_id": bson.ObjectId(),
                        "name": ll,
                        "description": "Match Label for InterfaceProfile",
                        "bg_color1": 15105570,
                        "bg_color2": 15965202,
                        "is_protected": False,
                        # Label scope
                        "enable_agent": False,
                        "enable_service": False,
                        "enable_serviceprofile": False,
                        "enable_managedobject": False,
                        "enable_managedobjectprofile": False,
                        "enable_administrativedomain": False,
                        "enable_authprofile": False,
                        "enable_commandsnippet": False,
                        "enable_allocationgroup": False,
                        "enable_networksegment": False,
                        "enable_object": False,
                        "enable_objectmodel": False,
                        "enable_platform": False,
                        "enable_resourcegroup": False,
                        "enable_sensorprofile": False,
                        # Exposition scope
                        "expose_metric": False,
                        "expose_managedobject": False,
                    }
                )
            ]
        if bulk:
            self.mongo_db["noc.interfaces"].bulk_write(bulk)
        if labels_bulk:
            self.mongo_db["labels"].bulk_write(labels_bulk)
