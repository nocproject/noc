# ----------------------------------------------------------------------
# Migration Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Iterable, Tuple
from pathlib import Path

# Third-party modules
import cachetools

# NOC modules
from noc.config import config
from noc.settings import INSTALLED_APPS
from .base import BaseMigration


class MigrationLoader(object):
    _migration_cache = {}

    @staticmethod
    def _iter_app_migration_files(app: str) -> Iterable[Tuple[str, bool]]:
        """
        Iterate over migration files.

        Merge with custom when necessary.

        Args:
            app: App name
        Returns:
            Yields tuple of migration name and boolean
                with True, if file belongs to the custom.
        """
        if config.path.custom_path:
            custom = Path(config.path.custom_path)
        else:
            custom = None
        for mp in config.get_customized_paths(app, "migrations"):
            root = Path(mp)
            is_custom = custom is not None and root.is_relative_to(custom)
            for f_name in root.rglob("*.py"):
                if f_name.stem == "__init__":
                    continue
                yield f"{app}.{f_name.stem}", is_custom

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_migration_cache"))
    def get_migration(cls, name: str, is_custom: bool = False) -> BaseMigration:
        """
        Get migration instance.

        Args:
            name: Migration name (i.e. `<app>.<name>`)
            is_custom: True, when migration is from custom
        Returns:
            Migration instance.
        """
        app, mname = name.split(".")
        if is_custom:
            mn = f"noc.custom.{app}.migrations.{mname}"
        else:
            mn = f"noc.{app}.migrations.{mname}"
        m = __import__(mn, {}, {}, "Migration")
        return m.Migration()

    @classmethod
    def iter_migration_names(cls) -> Iterable[str]:
        """
        Yield all available migration names
        """
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            app = app[4:]
            for name, _ in sorted(cls._iter_app_migration_files(app)):
                yield name

    @classmethod
    def iter_app_migrations(cls, app: str) -> Iterable[BaseMigration]:
        """
        Yield all migrations for application.

        Args:
            app: Application name.
        Returns:
            Yield migration instances.
        """
        prev_name = None
        for name, is_custom in sorted(cls._iter_app_migration_files(app)):
            migration = cls.get_migration(name, is_custom)
            if prev_name:
                # Implicit dependency from previous migration
                migration.add_dependency(prev_name)
            yield migration
            prev_name = migration.get_name()

    def iter_plan(self) -> Iterable[BaseMigration]:
        def iter_chain(app: str) -> Iterable[BaseMigration]:
            for m in self.iter_app_migrations(app):
                # Yield pending, if exists
                while app in pending:
                    yield pending.pop(app)
                # Yield next migration
                yield m
            while app in pending:
                yield pending.pop(app)

        seen = set()
        chains = {}  # app -> chain
        apps = []
        pending = {}  # app -> blocked migrations
        # Build application migration chains
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            app = app[4:]
            apps += [app]
            chains[app] = iter_chain(app)
        #
        while chains:
            l_seen = len(seen)
            for app in apps:
                if app not in chains:
                    continue  # Fully processed
                mc = 0
                for migration in chains[app]:
                    mc += 1
                    if migration.is_resolved(seen):
                        # Migration is ready to be applied
                        yield migration
                        seen.add(migration.get_name())
                        continue
                    # Migration is blocked, return to pending
                    pending[app] = migration
                    # Suspend application chain processing and switch to next application
                    break
                if not mc:
                    # No more migrations, stop application processing
                    del chains[app]
            if pending and l_seen == len(seen):
                # No migrations can further be resolved
                deps = ", ".join(pending[x].get_name() for x in pending)
                msg = f"Circular dependencies between {deps}"
                raise ValueError(msg)


loader = MigrationLoader()
