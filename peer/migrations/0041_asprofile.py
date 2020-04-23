# ----------------------------------------------------------------------
# ASProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson

# NOC module
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create default profile
        P_ID = "5ae04bcb45ce8300f385edb2"
        pcoll = self.mongo_db["asprofiles"]
        pcoll.insert_one(
            {"_id": bson.ObjectId(P_ID), "name": "default", "description": "Default Profile"}
        )
        # Create AS.profile
        self.db.add_column(
            "peer_as", "profile", DocumentReferenceField("peer.ASProfile", null=True, blank=True)
        )
        # Update profiles
        self.db.execute("UPDATE peer_as SET profile = %s", [P_ID])
        # Set profile not null
        self.db.execute("ALTER TABLE peer_as ALTER profile SET NOT NULL")
