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
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        self.db.create_table(
            "sa_objectstatus",
            (
                (
                    "managed_object",
                    models.OneToOneField(
                        ManagedObject,
                        verbose_name="Managed Object Reference",
                        unique=True,
                        primary_key=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "last",
                    models.DateTimeField(
                        "Last update Time", auto_now_add=True, null=True, blank=True
                    ),
                ),
                ("status", models.BooleanField("Status")),
            ),
        )
        # Migration ObjectStatus
        coll = self.mongo_db["noc.cache.object_status"]
        bulk = []
        # Getting all ManagedObjects for exclude constraints error
        mos = {row[0] for row in self.db.execute("SELECT id FROM sa_managedobject")}
        for row in coll.find({"object": {"$exists": True}}):
            if row["object"] not in mos:
                continue
            bulk += [(row["object"], row["status"], row.get("last"))]
        if bulk:
            cursor = connection.cursor()
            execute_values(
                cursor,
                """
                INSERT INTO sa_objectstatus as os (managed_object_id, status, last) VALUES %s
                ON CONFLICT (managed_object_id) DO NOTHING
                """,
                bulk,
                page_size=1000,
            )
