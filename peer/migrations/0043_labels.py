# ----------------------------------------------------------------------
# Migrate labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


from collections import defaultdict

# Third-party modules
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration
from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField


class Migration(BaseMigration):
    depends_on = [("vc", "0025_labels")]

    TAG_MODELS = [("peer_as", "asn"), ("peer_asset", "assetpeer"), ("peer_peer", "peer")]

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
                    # DNS
                    "enable_dnszone": False,
                    "enable_dnszonerecord": False,
                    # Peer
                    "enable_asn": False,
                    "enable_assetpeer": False,
                    "enable_peer": False,
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                }
                for setting in labels[label]:
                    doc[setting] = True
                bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
