# ----------------------------------------------------------------------
# ManagedObject Default workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Workflow
        db["workflows"].insert_one(
            {
                "_id": ObjectId("641a8634d97a4a87b46788a0"),
                "name": "ManagedObject Default",
                "is_active": True,
                "description": "ManagedObject Default Workflow",
                "bi_id": 2858828191196989734,
            }
        )
