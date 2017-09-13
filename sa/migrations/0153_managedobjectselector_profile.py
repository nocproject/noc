import uuid
from south.db import db
from django.db import models
from noc.core.model.fields import DocumentReferenceField
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        # Get profile record mappings
        pcoll = get_db()["noc.profiles"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # UPDATE profiles
        s_profiles = list(db.execute("SELECT DISTINCT filter_profile FROM sa_managedobjectselector"))
        for p, in s_profiles:
            if not p:
                continue
            db.execute("""
            UPDATE sa_managedobjectselector
            SET filter_profile = %s
            WHERE filter_profile = %s
            """, [pmap[p], p])
        # Alter .filter_profile column
        db.execute("ALTER TABLE sa_managedobjectselector ALTER filter_name TYPE CHAR(24) USING SUBSTRING(\"filter_name\", 1, 24)")
        # Create .filter_vendor field
        db.add_column(
            "sa_managedobjectselector",
            "filter_vendor",
            DocumentReferenceField(
                "inv.Vendor", null=True, blank=True
            )
        )
        # Create .filter_platform field
        db.add_column(
            "sa_managedobjectselector",
            "filter_platform",
            DocumentReferenceField(
                "inv.Vendor", null=True, blank=True
            )
        )
        # Create .filter_version field
        db.add_column(
            "sa_managedobjectselector",
            "filter_version",
            DocumentReferenceField(
                "inv.Firmware", null=True, blank=True
            )
        )
        # Create ..filter_tt_system field
        db.add_column(
            "sa_managedobjectselector",
            "filter_tt_system",
            DocumentReferenceField(
                "inv.Firmware", null=True, blank=True
            )
        )

    def backwards(self):
        pass
