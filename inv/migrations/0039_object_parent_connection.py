# ----------------------------------------------------------------------
# Convert vertical connections to parent/parent_name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Tuple, Optional, Any

# Third-party modules
from bson import ObjectId
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        def get_dir(doc: Dict[str, Any]) -> Optional[str]:
            o = doc.get("object")
            if not o:
                return None
            m = obj_models[o]
            n = doc.get("name")
            if not n:
                return None
            return conn_dirs[m, n]

        def is_inner(doc: Dict[str, Any]) -> bool:
            d = get_dir(doc)
            return not (d is None or d != "i")

        def is_outer(doc: Dict[str, Any]) -> bool:
            d = get_dir(doc)
            return not (d is None or d != "o")

        # Get connection directions
        om = self.mongo_db["noc.objectmodels"]
        conn_dirs: Dict[Tuple[ObjectId, str], str] = {}
        for doc in om.find({}, {"_id": 1, "connections": 1}):
            conns: List[Dict[str, Any]] = doc.get("connections")
            if not conns:
                continue
            for c in conns:
                conn_dirs[doc["_id"], c["name"]] = c["direction"]
        # Get object models
        oc = self.mongo_db["noc.objects"]
        obj_models: Dict[ObjectId, ObjectId] = {
            doc["_id"]: doc["model"] for doc in oc.find({}, {"_id": 1, "model": 1})
        }
        # Walk through connections
        to_prune: List[ObjectId] = []
        parent_bulk = []
        ocm = self.mongo_db["noc.objectconnections"]
        for oc in ocm.find({}, {"_id": 1, "connection": 1}):
            c: Optional[List[Dict[str, Any]]] = oc.get("connection")
            if not c or len(c) != 2:
                continue
            if is_inner(c[0]) and is_outer(c[1]):
                to_prune.append(oc["_id"])
                parent_bulk.append(
                    UpdateOne(
                        {"_id": c[1]["object"]},
                        {"$set": {"parent": c[0]["object"], "parent_connection": c[0]["name"]}},
                    )
                )
            elif is_outer(c[0]) and is_inner(c[1]):
                to_prune.append(oc["_id"])
                parent_bulk.append(
                    UpdateOne(
                        {"_id": c[0]["object"]},
                        {"$set": {"parent": c[1]["object"], "parent_connection": c[1]["name"]}},
                    )
                )
        # Update objects
        if parent_bulk:
            self.mongo_db["noc.objects"].bulk_write(parent_bulk)
        # Prune vertical connections
        if to_prune:
            self.mongo_db["noc.objectconnections"].delete_many({"_id": {"$in": to_prune}})
            print(f"{len(to_prune)} vertical connection has been refactored")
