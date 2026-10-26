# ----------------------------------------------------------------------
# Migration Runner
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from collections.abc import Iterator

# NOC modules
from noc.core.mongo.connection import get_db
from noc.settings import INSTALLED_APPS

from .base import BaseMigration, migration_loaders


class MigrationRunner:
    def __init__(self) -> None:
        self.db = get_db()
        self.hist_coll = self.db["migrations"]
        self.logger = logging.getLogger("migration")

    @staticmethod
    def iter_app_migrations(app: str) -> Iterator[BaseMigration]:
        """Yield an application's migrations in sequence order."""
        prev_name: str | None = None
        loader = migration_loaders[app]
        for migration_class in (loader[name] for name in loader):
            migration = migration_class()
            if prev_name:
                # Implicit dependency from previous migration
                migration.add_dependency(prev_name)
            yield migration
            prev_name = migration.get_name()

    @classmethod
    def iter_plan(cls) -> Iterator[BaseMigration]:
        """Yield migrations in dependency order."""

        def iter_chain(app: str) -> Iterator[BaseMigration]:
            for migration in cls.iter_app_migrations(app):
                while app in pending:
                    yield pending.pop(app)
                yield migration
            while app in pending:
                yield pending.pop(app)

        seen: set[str] = set()
        chains: dict[str, Iterator[BaseMigration]] = {}
        apps: list[str] = []
        pending: dict[str, BaseMigration] = {}
        for app in INSTALLED_APPS:
            if not app.startswith("noc.") or app[4:] not in migration_loaders:
                continue
            app = app[4:]
            apps.append(app)
            chains[app] = iter_chain(app)
        while chains:
            previous_seen: int = len(seen)
            for app in apps:
                if app not in chains:
                    continue
                has_migrations: bool = False
                for migration in chains[app]:
                    has_migrations = True
                    if migration.is_resolved(seen):
                        yield migration
                        seen.add(migration.get_name())
                        continue
                    pending[app] = migration
                    break
                if not has_migrations:
                    del chains[app]
            if pending and previous_seen == len(seen):
                deps = ", ".join(migration.get_name() for migration in pending.values())
                msg = f"Circular dependencies between {deps}"
                raise ValueError(msg)

    def migrate(self):
        self.logger.info("Migrating")
        applied = self.get_history()
        # Apply all pending migrations
        for migration in self.iter_plan():
            name = migration.get_name()
            if migration.is_applied(applied):
                continue  # Already applied, skip
            self.logger.info("Applying %s", name)
            ts = datetime.datetime.now()
            migration.migrate()
            delta = datetime.datetime.now() - ts
            applied.add(name)
            self.hist_coll.insert_one({"name": name, "ts": ts, "duration": delta.total_seconds()})
        self.logger.info("Done")

    def get_history(self) -> set[str]:
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
        # Third-party modules
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
        items = [{"name": f"{row[0]}.{row[1]}", "ts": row[2], "duration": 0.0} for row in cursor]
        # Convert legacy history
        self.hist_coll.insert_many(items)
        # Drop legacy history
        cursor.execute("DROP TABLE south_migrationhistory")
