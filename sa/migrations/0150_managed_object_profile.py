# ----------------------------------------------------------------------
# managedobject profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        # Select profile names
        profiles = {
            r[0] for r in self.db.execute("SELECT DISTINCT profile_name FROM sa_managedobject")
        }
        # Create profile records
        pcoll = self.mongo_db["noc.profiles"]
        for p in profiles:
            u = uuid.uuid4()
            pcoll.update_many(
                {"name": p}, {"$set": {"name": p}, "$setOnInsert": {"uuid": u}}, upsert=True
            )
        # Get profile record mappings
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # Create .profile field
        self.db.add_column(
            "sa_managedobject",
            "profile",
            DocumentReferenceField("inv.Profile", null=True, blank=True),
        )
        # Migrate profile data
        for p in profiles:
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET profile = %s
                WHERE profile_name = %s
            """,
                [pmap[p], p],
            )
            self.db.execute(
                """
                UPDATE sa_managedobjectselector
                SET filter_profile = %s
                WHERE filter_profile = %s
            """,
                [pmap[p], p],
            )
        # Set profile as not null
        self.db.execute("ALTER TABLE sa_managedobject ALTER profile SET NOT NULL")
        # Drop legacy profile_name
        self.db.delete_column("sa_managedobject", "profile_name")
