# ----------------------------------------------------------------------
# Create ManagedObject status table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

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
        suspended_jobs = defaultdict(list)
        # Getting all ManagedObjects for exclude constraints error
        mos = {row[0]: row[1] for row in self.db.execute("SELECT id, pool FROM sa_managedobject")}
        for row in coll.find({"object": {"$exists": True}}):
            if row["object"] not in mos:
                continue
            bulk += [(row["object"], row["status"], row.get("last"))]
            if not row["status"]:
                suspended_jobs[mos[row["object"]]].append(row["object"])
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
        pool_map = {str(p["_id"]): p["name"] for p in self.mongo_db["noc.pools"].find()}
        for pool, ids in suspended_jobs.items():
            pool = pool_map[pool]
            self.mongo_db[f"noc.schedules.discovery.{pool}"].update_many(
                {"key": {"$in": ids}},
                {"$set": {"s": "s"}},
            )
