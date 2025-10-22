# ----------------------------------------------------------------------
# Migrate labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


from collections import defaultdict

# Third-party modules
from pymongo import InsertOne, UpdateMany, UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("inv", "0021_labels")]

    TAG_COLLETIONS = [
        ("noc.subscribers", "subscriber"),
        ("noc.subscriberprofiles", "subscriberprofile"),
        ("noc.suppliers", "supplier"),
        ("noc.supplierprofiles", "supplierprofile"),
    ]

    def migrate(self):
        labels = defaultdict(set)  # label: settings
        # Mongo models
        for collection, setting in self.TAG_COLLETIONS:
            coll = self.mongo_db[collection]
            coll.bulk_write(
                [UpdateMany({"tags": {"$exists": True}}, {"$rename": {"tags": "labels"}})]
            )
            r = next(
                coll.aggregate(
                    [
                        {"$match": {"labels": {"$exists": True, "$ne": []}}},
                        {"$unwind": "$labels"},
                        {"$group": {"_id": 1, "all_labels": {"$addToSet": "$labels"}}},
                    ]
                ),
                None,
            )
            if r:
                for ll in r["all_labels"]:
                    labels[ll].add(f"enable_{setting}")
        # Unset tags
        for collection, setting in self.TAG_COLLETIONS:
            coll.bulk_write([UpdateMany({}, {"$unset": {"tags": 1}})])
        # Add labels
        self.sync_labels(labels)

    def sync_labels(self, labels):
        # Create labels
        bulk = []
        l_coll = self.mongo_db["labels"]
        current_labels = {ll["name"]: ll["_id"] for ll in l_coll.find()}
        for label in labels:
            if label in current_labels:
                bulk += [
                    UpdateOne(
                        {"_id": current_labels[label]},
                        {"$set": dict.fromkeys(labels[label], True)},
                    )
                ]
            else:
                doc = {
                    # "_id": bson.ObjectId(),
                    "name": label,
                    "description": "",
                    "bg_color1": 8359053,
                    "fg_color1": 16777215,
                    "bg_color2": 8359053,
                    "fg_color2": 16777215,
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
                    # CRM
                    "enable_subscriber": False,
                    "enable_subscriberprofile": False,
                    "enable_supplier": False,
                    "enable_supplierprofile": False,
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                }
                for setting in labels[label]:
                    doc[setting] = True
                bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
