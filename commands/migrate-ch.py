# ----------------------------------------------------------------------
# CH database schema migration tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.ensure import (
    ensure_bi_models,
    ensure_pm_scopes,
    ensure_dictionary_models,
    ensure_report_ds_scopes,
)
from noc.core.mongo.connection import connect as mongo_connect
from noc.config import config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--host", dest="host", help="ClickHouse address")
        parser.add_argument("--port", dest="port", type=int, help="ClickHouse port")
        parser.add_argument(
            "--force-type",
            dest="allow_type",
            action="store_true",
            default=False,
            help="Allow migrate column when type mismatch",
        )

    def handle(self, host=None, port=None, allow_type=False, *args, **options):
        self.host = host or None
        self.port = port or None
        self.connect()
        mongo_connect()
        self.ensure_db()
        self.create_dictionaries_db()
        changed = ensure_pm_scopes(connect=self.connect, allow_type=allow_type)
        changed |= ensure_bi_models(connect=self.connect, allow_type=allow_type)
        changed |= ensure_dictionary_models(connect=self.connect, allow_type=allow_type)
        changed |= ensure_report_ds_scopes(connect=self.connect, allow_type=allow_type)
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def connect(self):
        """
        Connect to database
        :return:
        """
        self.connect = connection(host=self.host, port=self.port, read_only=False)

    def ensure_db(self):
        """
        Ensure clickhouse database is exists
        :return:
        """
        self.print("Ensuring database")
        self.connect.ensure_db()

    def create_dictionaries_db(self):
        self.print("Ensuring Dictionary database")
        self.connect.execute(
            post="CREATE DATABASE IF NOT EXISTS dictionaries ENGINE = Dictionary", nodb=True
        )
        self.connect.execute(
            post=f"CREATE DATABASE IF NOT EXISTS {config.clickhouse.db_dictionaries}", nodb=True
        )


if __name__ == "__main__":
    Command().run()
