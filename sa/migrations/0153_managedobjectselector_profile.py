# ----------------------------------------------------------------------
# managedobjectselector profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        # Get profile record mappings
        pcoll = self.mongo_db["noc.profiles"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # UPDATE profiles
        s_profiles = list(
            self.db.execute("SELECT DISTINCT filter_profile FROM sa_managedobjectselector")
        )
        for (p,) in s_profiles:
            if not p:
                continue
            if p not in pmap:
                # If migrations on 0150_managed_object_profile
                continue
            self.db.execute(
                """
            UPDATE sa_managedobjectselector
            SET filter_profile = %s
            WHERE filter_profile = %s
            """,
                [pmap[p], p],
            )
        # Alter .filter_profile column
        self.db.execute(
            """
            ALTER TABLE sa_managedobjectselector
            ALTER filter_profile TYPE CHAR(24) USING SUBSTRING(\"filter_profile\", 1, 24)
            """
        )
        # Create .filter_vendor field
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_vendor",
            DocumentReferenceField("inv.Vendor", null=True, blank=True),
        )
        # Create .filter_platform field
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_platform",
            DocumentReferenceField("inv.Vendor", null=True, blank=True),
        )
        # Create .filter_version field
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_version",
            DocumentReferenceField("inv.Firmware", null=True, blank=True),
        )
        # Create .filter_tt_system field
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_tt_system",
            DocumentReferenceField("inv.Firmware", null=True, blank=True),
        )
