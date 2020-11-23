# ----------------------------------------------------------------------
# Set sharding keys into scheduler jobs
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.mongo.connection import get_db


def fix() -> None:
    db = get_db()
    for cname in db.list_collection_names():
        if not cname.startswith("noc.schedules.correlator."):
            continue
        print(f"Fixing {cname}:")
        coll = db[cname]
        r = coll.update_many({"shard": {"$exists": False}}, {"$set": {"shard": 0}})
        if r.modified_count:
            print(f"  {r.modified_count} schedules have been fixed")
        else:
            print("  Nothing to fix")
