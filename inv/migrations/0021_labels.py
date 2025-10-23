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
    depends_on = [("sa", "0213_labels")]

    OBJECTMODEL_TAGS = {
        "noc::inv::chassis": "Chassis (equipment body)",
        "noc::inv::lc": "Linecard, optional replaceable module (except for fans and PSU)",
        "noc::inv::xcvr": "Transceiver",
        "noc::inv::psu": "Power supply unit",
        "noc::inv::sup": "Supervisor or control module (control plane)",
        "noc::inv::fabric": "Commutation fabric (data plane)",
        "noc::inv::fan": "Fan",
        "noc::inv::soft": "Software component",
        "noc::inv::port": "Contains ports acceptable for client connection either directly or via transceiver",
        "noc::inv::dsp": "Digital signal processor for voice/video processing",
    }

    TAG_COLLETIONS = [
        ("allocationgroups", "allocationgroup"),
        ("noc.networksegments", "networksegment"),
        ("noc.objects", "object"),
        ("inv.platforms", "platform"),
        ("resourcegroups", "resourcegroup"),
        ("sensorprofiles", "sensorprofile"),
    ]

    def migrate(self):
        labels = defaultdict(set)  # label: settings

        coll = self.mongo_db["noc.objectmodels"]
        bulk = []
        # ObjectModel Migrate
        coll.bulk_write([UpdateMany({"tags": {"$exists": True}}, {"$rename": {"tags": "labels"}})])
        for item in coll.aggregate(
            [
                {"$match": {"labels": {"$exists": True, "$ne": []}}},
                {
                    "$addFields": {
                        "l2": {
                            "$map": {
                                "input": "$labels",
                                "as": "label",
                                "in": {"$concat": ["noc::inv::", "$$label"]},
                            }
                        }
                    }
                },
                {"$project": {"l2": 1}},
            ]
        ):
            if not item.get("l2"):
                continue
            ll = set(item["l2"]).intersection(set(self.OBJECTMODEL_TAGS))
            bulk += [UpdateOne({"_id": item["_id"]}, {"$set": {"labels": list(ll)}})]
        if bulk:
            coll.bulk_write(bulk)
        self.sync_om_labels()
        # Mongo models
        for collection, setting in self.TAG_COLLETIONS:
            coll = self.mongo_db[collection]
            coll.bulk_write(
                [UpdateMany({"tags": {"$exists": True}}, {"$rename": {"tags": "labels"}})]
            )
            r = next(
                coll.aggregate(
                    [
                        {"$match": {"tags": {"$exists": True, "$ne": []}}},
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
                    "bg_color2": 8359053,
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
                for setting in labels[label]:
                    doc[setting] = True
                bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)

    def sync_om_labels(self):
        # Sync ObjectModels Label
        # noc::inv::xcvr
        l_coll = self.mongo_db["labels"]
        bulk = [
            UpdateOne(
                {"name": "noc::inv::*"},
                {
                    "$set": {
                        # "_id": bson.ObjectId(),
                        "name": "noc::inv::*",
                        "description": "Internal scope for Inventory tags",
                        "bg_color1": 15965202,
                        "bg_color2": 2719929,
                        "is_protected": True,
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
                        "enable_objectmodel": True,
                        "enable_platform": False,
                        "enable_resourcegroup": False,
                        "enable_sensorprofile": False,
                        # Exposition scope
                        "expose_metric": False,
                        "expose_datastream": False,
                    }
                },
                upsert=True,
            )
        ]
        for label in self.OBJECTMODEL_TAGS:
            bulk += [
                InsertOne(
                    {
                        # "_id": bson.ObjectId(),
                        "name": label,
                        "description": self.OBJECTMODEL_TAGS[label],
                        "bg_color1": 15965202,
                        "fg_color1": 16777215,
                        "bg_color2": 2719929,
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
                        "enable_objectmodel": True,
                        "enable_platform": False,
                        "enable_resourcegroup": False,
                        "enable_sensorprofile": False,
                        # Exposition scope
                        "expose_metric": False,
                        "expose_datastream": False,
                    }
                )
            ]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
