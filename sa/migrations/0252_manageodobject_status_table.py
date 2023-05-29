# ----------------------------------------------------------------------
# Create ManagedObject status table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
from django.db import connection
from psycopg2.extras import execute_values

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'Task'
        self.db.create_table(
            "sa_objectstatus",
            (
                (
                    "managed_object_id",
                    models.IntegerField("Managed Object Reference", unique=True, primary_key=True),
                ),
                ("last", models.DateTimeField("Last update Time", auto_now_add=True)),
                ("status", models.BooleanField("Status")),
            ),
        )
        # Migration ObjectStatus
        coll = self.mongo_db["noc.cache.object_status"]
        bulk = []
        for row in coll.find({"object": {"$exists": True}}):
            bulk += [(row["object"], row["status"], row.get("last"))]
        if bulk:
            cursor = connection.cursor()
            execute_values(
                cursor,
                """
                INSERT INTO sa_objectstatus as os (managed_object, status, last) VALUES %s
                ON CONFLICT (managed_object) DO NOTHING
                """,
                bulk,
                page_size=1000,
            )
