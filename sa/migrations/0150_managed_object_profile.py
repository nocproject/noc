import uuid

from noc.core.model.fields import DocumentReferenceField
from noc.lib.nosql import get_db
from south.db import db


class Migration:
    def forwards(self):
        # Select profile names
        profiles = set(r[0] for r in db.execute("SELECT DISTINCT profile_name FROM sa_managedobject"))
        # Create profile records
        pcoll = get_db()["noc.profiles"]
        for p in profiles:
            u = uuid.uuid4()
            pcoll.update({
                "name": p
            }, {
                "$set": {
                    "name": p
                },
                "$setOnInsert": {
                    "uuid": u
                }
            }, upsert=True)
        # Get profile record mappings
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = str(d["_id"])
        # Create .profile field
        db.add_column(
            "sa_managedobject",
            "profile",
            DocumentReferenceField(
                "inv.Profile", null=True, blank=True
            )
        )
        # Migrate profile data
        for p in profiles:
            db.execute("""
                UPDATE sa_managedobject
                SET profile = %s
                WHERE profile_name = %s 
            """, [pmap[p], p])
        # Set profile as not null
        db.execute("ALTER TABLE sa_managedobject ALTER profile SET NOT NULL")
        # Drop legacy profile_name
        db.delete_column("sa_managedobject", "profile_name")

    def backwards(self):
        pass
