import uuid
from south.db import db
from django.db import models
from noc.core.model.fields import DocumentReferenceField
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        #
        # Vendor
        #

        # Select vendors
        vendors = set(r[0] for r in db.execute("SELECT DISTINCT value FROM sa_managedobjectattribute WHERE key = 'vendor'"))
        # Create vendors records
        pcoll = get_db()["noc.vendors"]
        for v in vendors:
            u = uuid.uuid4()
            vc = v.upper()
            pcoll.update({
                "code": vc
            }, {
                "$set": {
                    "code": vc
                },
                "$setOnInsert": {
                    "name": v,
                    "uuid": u
                }
            }, upsert=True)
        # Get vendor record mappings
        vmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "code": 1}):
            vmap[d["code"]] = str(d["_id"])
        # Create .vendor field
        db.add_column(
            "sa_managedobject",
            "vendor",
            DocumentReferenceField(
                "inv.Vendor", null=True, blank=True
            )
        )
        # Migrate profile data
        for v in vendors:
            db.execute("""
                UPDATE sa_managedobject
                SET vendor = %s
                WHERE
                  id IN (
                    SELECT managed_object_id
                    FROM sa_managedobjectattribute
                    WHERE
                      key = 'vendor'
                      AND value = %s
                  )
            """, [vmap[v.upper()], v])

    def backwards(self):
        pass
