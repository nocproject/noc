# ---------------------------------------------------------------------
# Initialize inventory hierarchy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    ROOT_UUID = "0f1b7c90-c611-4046-9a83-b120377eb6e0"
    LOST_N_FOUND_UUID = "b0fae773-b214-4edf-be35-3468b53b03f2"

    def migrate(self):
        db = self.mongo_db
        # Initialize container models
        om = db.noc.objectmodels
        root = om.find_one({"name": "Root"})
        if not root:
            print("    Create Root model stub")
            root = om.insert_one(
                {"name": "Root", "uuid": self.ROOT_UUID, "data": {"container": {"container": True}}}
            )
            root = root.inserted_id
        else:
            root = root["_id"]
        lost_and_found = om.find_one({"name": "Lost&Found"})
        if not lost_and_found:
            print("    Create Lost&Found model stub")
            lost_and_found = om.insert_one(
                {
                    "name": "Lost&Found",
                    "uuid": self.LOST_N_FOUND_UUID,
                    "data": {"container": {"container": True}},
                }
            )
            lost_and_found = lost_and_found.inserted_id
        else:
            lost_and_found = lost_and_found["_id"]
        # Create root object
        objects = db.noc.objects
        r = objects.insert_one({"name": "Root", "model": root})
        r = r.inserted_id
        lf = objects.insert_one(
            {"name": "Global Lost&Found", "model": lost_and_found, "container": r}
        )
        lf = lf.inserted_id
        # Find all outer connection names
        m_c = {}
        containers = set()
        for m in db.noc.objectmodels.find():
            m_c[m["_id"]] = set(
                c["name"] for c in m.get("connections", []) if c["direction"] == "o"
            )
            if m.get("data", {}).get("container", {}).get("container", False):
                containers.add(m["_id"])
        # Assign all unconnected objects to l&f
        for o in db.noc.objects.find():
            if o["model"] in containers:
                continue
            found = False
            oc = m_c[o["model"]]
            if oc:
                for c in db.noc.objectconnections.find({"connection.object": o["_id"]}):
                    for cc in c["connection"]:
                        if cc["name"] in oc and cc["object"] == o["_id"]:
                            found = True
                            break
            if not found:
                # Set container
                db.noc.objects.update_many({"_id": o["_id"]}, {"$set": {"container": lf}})
