# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Migration Runner
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import datetime
# NOC modules
from noc.lib.nosql import get_db
from .loader import MigrationLoader


class MigrationRunner(object):
    def __init__(self):
        self.db = get_db()
        self.hist_coll = self.db["migrations"]
        self.logger = logging.getLogger("migration")

    def migrate(self):
        self.django_migrate()
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
            self.hist_coll.insert_one({
                "name": name,
                "ts": ts,
                "duration": delta.total_seconds()
            })
        self.logger.info("Done")

    def django_migrate(self):
        """
        Django syncdb/migrate call
        :return:
        """
        self.logger.info("Django migrations")
        from django.apps import apps
        # Leave only django's applications
        to_mask_apps = apps.apps_ready
        # Leave only django's applications before running migrate
        if to_mask_apps:
            installed_apps = [
                app.name for app in apps.get_app_configs()
                if not app.name.startswith("noc.") or app.name == "noc.aaa"]
            apps.set_available_apps(installed_apps)
        else:
            from noc.settings import INSTALLED_APPS
            installed_apps = [
                app for app in INSTALLED_APPS
                if not app.startswith("noc.") or app == "noc.aaa"]
            apps.populate(installed_apps)
        # Run django's migrate
        from django.core.management.commands.migrate import Command
        try:
            Command().execute(interactive=False, load_initial_data=False, verbosity="1", database="default")
        finally:
            if to_mask_apps:
                apps.unset_available_apps()

    def get_history(self):
        """
        Get set of performed migration names
        :return:
        """
        self.convert_south_history()
        return set(d["name"] for d in self.hist_coll.find({}, {"name": 1}))

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
            "SELECT app_name, migration, applied "
            "FROM south_migrationhistory "
            "ORDER BY id"
        )
        items = [{
            "name": "%s.%s" % (row[0], row[1]),
            "ts": row[2],
            "duration": 0.0
        } for row in cursor]
        # Convert legacy history
        self.hist_coll.insert_many(items)
        # Drop legacy history
        cursor.execute("DROP TABLE south_migrationhistory")
