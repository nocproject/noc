## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Postgres probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
try:
    import psycopg2
except ImportError:
    psycopg2 = None
## NOC modules
from noc.pm.probes.base import Probe, metric


class PostgresProbe(Probe):
    TITLE = "Postgres"
    DESCRIPTION = "Postgres server statistics"
    TAGS = ["db", "postgres"]
    CONFIG_FORM = "PostgresConfig"

    @metric([
        "DB | Transaction | Commit", "DB | Transaction | Rollback",
        "DB | Deadlocks",
        "Postgres | Tuples | Returned", "Postgres | Tuples | Fetched",
        "Postgres | Tuples | Inserted", "Postgres | Tuples | Updated",
        "Postgres | Tuples | Deleted"
    ], convert=metric.DERIVE, preference=metric.PREF_PLATFORM)
    @metric([
        "DB | Connections | Current",
        "DB | Size | Total"
    ], convert=metric.NONE, preference=metric.PREF_PLATFORM)
    def get_db_stats(self, host, database, port=None, user=None, password=None):
        if not psycopg2:
            self.logger.error("psycopg2 is not installed. Disabling probe")
            self.disable()
            return
        connect = psycopg2.connect(
            database=database, host=host, port=port,
            user=user, password=password
        )
        cursor = connect.cursor()
        cursor.execute(
            """
            SELECT numbackends, xact_commit, xact_rollback,
                tup_returned, tup_fetched, tup_inserted,
                tup_updated, tup_deleted, deadlocks,
                pg_database_size(%s) as dbsize
            FROM pg_stat_database WHERE datname = %s
            """,
            [database, database]
        )
        (numbackends, xact_commit, xact_rollback,
         tup_returned, tup_fetched, tup_inserted,
         tup_updated, tup_deleted, deadlocks, dbsize) = cursor.fetchone()
        return {
            "DB | Transaction | Commit": xact_commit,
            "DB | Transaction | Rollback": xact_rollback,
            "DB | Connections | Current": numbackends,
            "DB | Deadlocks": deadlocks,
            "DB | Size | Total": dbsize,
            "Postgres | Tuples | Returned": tup_returned,
            "Postgres | Tuples | Fetched": tup_fetched,
            "Postgres | Tuples | Inserted": tup_inserted,
            "Postgres | Tuples | Updated": tup_updated,
            "Postgres | Tuples | Deleted": tup_deleted
        }
