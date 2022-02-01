# ----------------------------------------------------------------------
# Migrate ObjectData
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create uplinks fields
        coll = self.mongo_db["noc.objectdata"]
        for data in coll.find({}):
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET uplinks = %s, rca_neighbors = %s, dlm_windows = %s,
                adm_path = %s, segment_path = %s, container_path = %s
                WHERE id = %s
                """,
                [
                    data.get("uplinks", []),
                    data.get("rca_neighbors", []),
                    data.get("dlm_windows", []),
                    data.get("adm_path", []),
                    [str(x) for x in data.get("segment_path", [])],
                    [str(x) for x in data.get("container_path", [])],
                    data["_id"],
                ],
            )
