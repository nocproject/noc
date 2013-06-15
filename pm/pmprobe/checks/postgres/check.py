## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PostgresCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Contrib modules
import psycopg2
## NOC modules
from noc.pm.pmprobe.checks.base import BaseCheck, Counter, Gauge
from noc.sa.interfaces.base import StringParameter, IntParameter


class PostgresCheck(BaseCheck):
    name = "postgres"

    description = """
        PostgreSQL database monitoring
    """

    parameters = {
        "db": StringParameter(),
        "host": StringParameter(required=False),
        "port": IntParameter(required=False),
        "user": StringParameter(required=False),
        "password": StringParameter(required=False)
    }

    time_series = [
        Gauge("num_backends"),
        Counter("xact_commit"),
        Counter("xact_rollback"),
        Counter("blocks_fetched"),
        Counter("blocks_hit"),
        Counter("records_returned"),
        Counter("records_fetched"),
        Counter("records_inserted"),
        Counter("records_updated"),
        Counter("records_deleted")
    ]

    form = "NOC.pm.check.postgres.PostgresCheckForm"

    PG_STAT_DATABASE_COUNTERS = {
        "numbackends": "num_backends",
        "xact_commit": "xact_commit",
        "xact_rollback": "xact_rollback",
        "blks_read": "blocks_fetched",
        "blks_hit": "blocks_hit",
        "tup_returned": "records_returned",
        "tup_fetched": "records_fetched",
        "tup_inserted": "records_inserted",
        "tup_updated": "records_updated",
        "tup_deleted": "records_deleted",
    }

    def handle(self):
        try:
            connect = psycopg2.connect(
                database=self.config["db"],
                host=self.config.get("host"),
                port=self.config.get("port"),
                user=self.config.get("user"),
                password=self.config.get("password")
            )
        except psycopg2.OperationalError, why:
            self.error("Database connection failed: %s" % why)
            return None
        cursor = connect.cursor()
        flist = list(self.PG_STAT_DATABASE_COUNTERS)
        query = "SELECT %s FROM pg_stat_database WHERE datname = '%s'" % (
            ", ".join(flist),
            self.config["db"]
        )
        cursor.execute(query)
        row = cursor.fetchone()
        if not row:
            self.error("Failed to fetch stats for database: %s" % self.config["db"])
            return None
        return dict((self.PG_STAT_DATABASE_COUNTERS[k], v)
                    for k, v in zip(flist, row))
