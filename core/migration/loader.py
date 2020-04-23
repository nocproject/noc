# ----------------------------------------------------------------------
# Migration Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import operator

# Third-party modules
import cachetools

# NOC modules
from noc.config import config
from noc.settings import INSTALLED_APPS


class MigrationLoader(object):
    _migration_cache = {}

    def __init__(self):
        pass

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_migration_cache"))
    def get_migration(cls, name):
        """
        Get migration instance
        :param name: Migration name
        :return:
        """
        app, mname = name.split(".")
        # @todo: Consider custom
        m = __import__("noc.%s.migrations.%s" % (app, mname), {}, {}, "Migration")
        assert m
        return m.Migration()

    def iter_migration_names(self):
        """
        Yield all available migration names
        :return:
        """
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            app = app[4:]
            for path in config.get_customized_paths(app, "migrations"):
                if not os.path.isdir(path):
                    continue
                for f_name in sorted(os.listdir(path)):
                    if f_name == "__init__.py" or not f_name.endswith(".py"):
                        continue
                    yield "%s.%s" % (app, f_name[:-3])

    def iter_app_migrations(self, app):
        """
        Yield all migrations for application
        :param app:
        :return:
        """
        prev_name = None
        for path in config.get_customized_paths(app, "migrations"):
            if not os.path.isdir(path):
                continue
            for f_name in sorted(os.listdir(path)):
                if f_name == "__init__.py" or not f_name.endswith(".py"):
                    continue
                migration = self.get_migration("%s.%s" % (app, f_name[:-3]))
                if prev_name:
                    migration.add_dependency(prev_name)
                yield migration
                prev_name = migration.get_name()

    def iter_plan(self):
        def iter_chain(app):
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
                raise ValueError(
                    "Circular dependencies between %s"
                    % ", ".join(pending[x].get_name() for x in pending)
                )


loader = MigrationLoader()
