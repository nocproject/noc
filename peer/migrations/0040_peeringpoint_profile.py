# ----------------------------------------------------------------------
# as profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0150_managed_object_profile")]

    def migrate(self):
        # Get profile record mappings
        pcoll = self.mongo_db["noc.profiles"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # Create .profile column
        self.db.add_column(
            "peer_peeringpoint",
            "profile",
            DocumentReferenceField("sa.Profile", null=True, blank=True),
        )
        # Update profiles
        for (p,) in list(self.db.execute("SELECT DISTINCT profile_name FROM peer_peeringpoint")):
            self.db.execute(
                """
            UPDATE peer_peeringpoint
            SET profile = %s
            WHERE profile_name = %s
            """,
                [pmap.get(p, pmap["Generic.Host"]), p],
            )
        # Set profile as not null
        self.db.execute("ALTER TABLE peer_peeringpoint ALTER profile SET NOT NULL")
        # Drop legacy profile_name
        self.db.delete_column("peer_peeringpoint", "profile_name")
