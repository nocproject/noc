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
    CONFIG_FORM = [
        {
            "name": "host",
            "xtype": "textfield",
            "fieldLabel": "Host",
            "allowBlank": False,
            "uiStyle": "medium"
        },
        {
            "name": "port",
            "xtype": "numberfield",
            "fieldLabel": "Port",
            "allowBlank": True,
            "uiStyle": "small",
            "hideTrigger": True
        },
        {
            "name": "database",
            "xtype": "textfield",
            "fieldLabel": "database",
            "allowBlank": False,
            "uiStyle": "medium"
        },
        {
            "name": "user",
            "xtype": "textfield",
            "fieldLabel": "user",
            "allowBlank": True,
            "uiStyle": "medium"
        },
        {
            "name": "password",
            "xtype": "textfield",
            "fieldLabel": "password",
            "allowBlank": True,
            "uiStyle": "medium"
        }
    ]

    DB_STATS_FIELDS = {
        "numbackends":  "DB | Connections | Current",
        "xact_commit": "DB | Transaction | Commit",
        "xact_rollback": "DB | Transaction | Rollback",
        "tup_returned": "Postgres | Tuples | Returned",
        "tup_fetched":  "Postgres | Tuples | Fetched",
        "tup_inserted": "Postgres | Tuples | Inserted",
        "tup_updated": "Postgres | Tuples | Updated",
        "tup_deleted": "Postgres | Tuples | Deleted",
        "deadlocks": "DB | Deadlocks"
    }

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
        if not hasattr(self, "stats_sql"):
            # Auto-detect available fields
            cursor.execute("""
                SELECT a.attname
                FROM pg_attribute a
                    JOIN pg_class c ON (a.attrelid = c.oid)
                WHERE c.relname = 'pg_stat_database'
            """)
            fields = []
            self.stats_metrics = []
            for a, in cursor.fetchall():
                if a in self.DB_STATS_FIELDS:
                    fields += [a]
                    self.stats_metrics += [self.DB_STATS_FIELDS[a]]
            # Add database size
            fields += ["pg_database_size(%s) as dbsize"]
            self.stats_metrics += ["DB | Size | Total"]
            #
            self.stats_sql = "SELECT %s FROM pg_stat_database WHERE datname = %%s" % ", ".join(fields)
            self.stats_args = [database, database]
            # self.reset_timer()
        cursor.execute(self.stats_sql, self.stats_args)
        result = cursor.fetchone()
        return dict((k, v) for k, v in zip(self.stats_metrics, result))

