# ----------------------------------------------------------------------
# Remove connections to renamed slots
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, List, Set

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Get model connections
        model_conns: Dict[ObjectId, Set[str]] = set()
        for doc in self.mongo_db["noc.objectmodels"].find({}, {"_id": 1, "connections": 1}):
            conns = doc.get("connections")
            if not conns:
                continue
            model_conns[doc["_id"]] = {c["name"] for c in conns}
        # Get object models
        obj_models: Dict[ObjectId, ObjectId] = {
            doc["_id"]: doc["model"]
            for doc in self.mongo_db["noc.objects"].find({}, {"_id": 1, "model": 1})
        }
        # Process connections
        to_prune: List[ObjectId] = []
        for doc in self.mongo_db["noc.objectconnections"].find({}, {"_id": 1, "connection": 1}):
            conns = doc.get("connection")
            if not doc:
                continue
            conn_id = doc["_id"]
            for cc in conns:
                obj_id = cc.get("object")
                if not obj:
                    print(f"Connection without object: {doc}")
                    to_prune.append(conn_id)
                    break
                c_name = cc.get("name")
                if not c_name:
                    print(f"Nameless connection: {doc}")
                    to_prune.append(conn_id)
                    break
                obj_model = obj_models.get(obj_id)
                if not obj_models:
                    print(f"Connection to deleted object: {doc}")
                    to_prune.append(conn_id)
                    break
                names = model_conns.get(obj_model)
                if not names:
                    print(f"Unknown object model: {doc}")
                    to_prune.append(conn_id)
                    break
                if c_name not in names:
                    print(f"Renamed connection {c_name}: {doc}. Available names {names}")
                    to_prune.append(conn_id)
                    break
        if to_prune:
            print(f"Deleting {len(to_prune)} broken connections")
            self.mongo_db["noc.objectconnections"].delete_many({"_id": {"$in": to_prune}})
