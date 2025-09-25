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
from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField


class Migration(BaseMigration):
    TAG_MODELS = [
        ("sa_managedobject", "managedobject"),
        ("sa_managedobjectprofile", "managedobjectprofile"),
        ("sa_administrativedomain", "administrativedomain"),
        ("sa_authprofile", "authprofile"),
        ("sa_commandsnippet", "commandsnippet"),
    ]
    TAG_COLLETIONS = [
        ("noc.services", "service"),
        ("noc.serviceprofiles", "serviceprofile"),
    ]

    def migrate(self):
        labels = defaultdict(set)  # label: settings
        # Create labels fields
        for table, setting in self.TAG_MODELS:
            self.db.add_column(
                table,
                "labels",
                ArrayField(CharField(max_length=250), null=True, blank=True, default=lambda: "{}"),
            )
            self.db.add_column(
                table,
                "effective_labels",
                ArrayField(CharField(max_length=250), null=True, blank=True, default=lambda: "{}"),
            )
        # Migrate data
        for table, setting in self.TAG_MODELS:
            self.db.execute(
                """
                UPDATE %s
                SET labels = tags
                WHERE tags is not NULL and tags <> '{}'
                """
                % table
            )
            # Fill labels
            for (ll,) in self.db.execute(
                """
                SELECT DISTINCT labels
                FROM %s
                WHERE labels <> '{}'
                """
                % table
            ):
                for name in ll:
                    labels[name].add(f"enable_{setting}")
        # Delete tags
        for table, setting in self.TAG_MODELS:
            self.db.delete_column(
                table,
                "tags",
            )
        # Create indexes
        for table, setting in self.TAG_MODELS:
            self.db.execute(f'CREATE INDEX x_{table}_labels ON "{table}" USING GIN("labels")')
            self.db.execute(
                f'CREATE INDEX x_{table}_effective_labels ON "{table}" USING GIN("effective_labels")'
            )
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
        # Migrate selector

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
                        {"$set": {setting: True for setting in labels[label]}},
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
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                }
                for setting in labels[label]:
                    doc[setting] = True
                bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
