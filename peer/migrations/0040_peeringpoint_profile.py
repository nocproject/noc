from south.db import db
from noc.lib.nosql import get_db
from noc.core.model.fields import DocumentReferenceField


class Migration:
    depends_on = [
        ("sa", "0150_managed_object_profile")
    ]

    def forwards(self):
        # Get profile record mappings
        pcoll = get_db()["noc.profiles"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # Create .profile column
        db.add_column(
            "peer_peeringpoint",
            "profile",
            DocumentReferenceField(
                "sa.Profile", null=True, blank=True
            )
        )
        # Update profiles
        for p, in list(db.execute("SELECT DISTINCT profile_name FROM peer_peeringpoint")):
            db.execute("""
            UPDATE peer_peeringpoint
            SET profile = %s
            WHERE profile_name = %s
            """, [pmap[p], p])
        # Set profile as not null
        db.execute("ALTER TABLE peer_peeringpoint ALTER profile SET NOT NULL")
        # Drop legacy profile_name
        db.delete_column("peer_peeringpoint", "profile_name")

    def backwards(self):
        pass
