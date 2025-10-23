# ----------------------------------------------------------------------
# Migration Runner
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime

# NOC modules
from noc.core.mongo.connection import get_db
from .loader import MigrationLoader


class MigrationRunner(object):
    def __init__(self):
        self.db = get_db()
        self.hist_coll = self.db["migrations"]
        self.logger = logging.getLogger("migration")

    def migrate(self):
        self.logger.info("Migrating")
        applied = self.get_history()
        loader = MigrationLoader()
        # Apply all pending migrations
        for migration in loader.iter_plan():
            name = migration.get_name()
            if name in applied:
                continue  # Already applied, skip
            self.logger.info("Applying %s", name)
            ts = datetime.datetime.now()
            migration.migrate()
            delta = datetime.datetime.now() - ts
            applied.add(name)
            self.hist_coll.insert_one({"name": name, "ts": ts, "duration": delta.total_seconds()})
        self.logger.info("Done")

    def get_history(self):
        """
        Get set of performed migration names
        :return:
        """
        self.convert_south_history()
        return {d["name"] for d in self.hist_coll.find({}, {"name": 1})}

    def convert_south_history(self):
        """
        Convert south_migrationhistory
        :return:
        """
        from django.db import connection

        cursor = connection.cursor()
        # Check south_migrationhistory is exists
        cursor.execute(
            "SELECT count(*) "
            "FROM pg_class "
            "WHERE relname = 'south_migrationhistory' AND relkind = 'r'"
        )
        count = cursor.fetchall()[0][0]
        if not count:
            return
        # Get legacy history
        self.logger.info("Migrating legacy history")
        cursor.execute(
            "SELECT app_name, migration, applied FROM south_migrationhistory ORDER BY id"
        )
        items = [
            {"name": "%s.%s" % (row[0], row[1]), "ts": row[2], "duration": 0.0} for row in cursor
        ]
        # Convert legacy history
        self.hist_coll.insert_many(items)
        # Drop legacy history
        cursor.execute("DROP TABLE south_migrationhistory")
