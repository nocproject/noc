# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CH database schema migration tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.ensure import ensure_bi_models, ensure_pm_scopes


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-h", "--host",
            dest="host",
            help="ClickHouse address"
        )
        parser.add_argument(
            "-p", "--port",
            dest="port",
            type=int,
            help="ClickHouse port"
        )

    def handle(self, host=None, port=None, *args, **options):
        self.host = host or None
        self.port = port or None
        self.connect()
        self.ensure_db()
        changed = ensure_bi_models(connection=self.connection)
        changed |= ensure_pm_scopes(connection=self.connection)
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def connect(self):
        """
        Connect to database
        :return:
        """
        self.connect = connection(host=self.host, port=self.port)

    def ensure_db(self):
        """
        Ensure clickhouse database is exists
        :return:
        """
        self.print("Ensuring database")
        self.connect.ensure_db()


if __name__ == "__main__":
    Command().run()
