# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PowerDNS SQL channel
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from ..dns import DNSZoneSyncHandler
from noc.sa.interfaces.base import StringParameter


class PowerDNSSQLHandler(DNSZoneSyncHandler):
    config = {
        "dbtype": StringParameter(choices=["postgres", "mysql", "sqlite"]),
        "dsn": StringParameter(),
        "domains_table": StringParameter(default="domains"),
        "records_table": StringParameter(default="records")
    }

    def configure(self, dbtype, dsn, domains_table, records_table,
                  **kwargs):
        if not hasattr(self, "connect_%s" % dbtype):
            raise ValueError("Invalid dbtype '%s'" % dbtype)
        self.connect = getattr(self, "connect_%s" % dbtype)
        self.dsn = dsn
        self.domains_table = domains_table
        self.records_table = records_table

    def connect_postgres(self):
        import psycopg2
        self.allow_questions = False
        return psycopg2.connect(dsn=self.dsn)

    def connect_mysql(self):
        import MySQLdb
        self.allow_questions = True
        dbc = dict(x.split("=", 1) for x in self.dsn.split())
        return MySQLdb.connect(**dbc)

    def connect_sqlite(self):
        import sqlite3
        self.allow_questions = True
        return sqlite3.connect(self.dsn, isolation_level=None)

    def cursor(self):
        self.logger.debug("Creating cursor")
        return self.connect().cursor()

    def execute(self, sql, args=[]):
        if not hasattr(self, "_cursor"):
            self._cursor = None
        if not self._cursor:
            self._cursor = self.cursor()
            self.logger.debug("SQL: BEGIN")
            self._cursor.execute("BEGIN")
        sql = sql.replace("RECORDS", self.records_table)
        sql = sql.replace("DOMAINS", self.domains_table)
        if not self.allow_questions:
            sql = sql.replace("?", "%s")
        self.logger.debug("SQL: %s %s", sql, args)
        self._cursor.execute(sql, args)
        if sql.upper() in ("COMMIT", "ROLLBACK"):
            self.logger.debug("Releasing cursor")
            self._cursor = None
        if sql.upper().startswith("SELECT"):
            d = self._cursor.fetchall()
            self.logger.debug("%d records fetched", len(d))
            return d
        else:
            return None

    def update_zone(self, uuid, zone, serial, records):
        acc = "NOC:%s" % uuid
        # Check zone is already exists
        d = self.execute(
            "SELECT id, notified_serial "
            "FROM DOMAINS "
            "WHERE name = ?",
            [zone]
        )
        if d:
            # Update zone
            zone_id, z_serial = d[0]
            if z_serial == serial:
                self.execute("COMMIT")
                return  # Not changed
            self.logger.info("Updating zone %s (%s)", zone, serial)
            self.execute(
                "UPDATE DOMAINS "
                "SET notified_serial = ? "
                "WHERE id = ?",
                [serial, zone_id]
            )
            # Fetch existing records
            existing = set(
                self.execute(
                    "SELECT name, type, content, ttl, prio "
                    "FROM RECORDS "
                    "WHERE domain_id = ?",
                    [zone_id]
                )
            )
        else:
            self.logger.info("Creating zone %s (%s)", zone, serial)
            # Create zone
            self.execute(
                "INSERT INTO DOMAINS(name, type, notified_serial, account) "
                "VALUES(?, ?, ?, ?)",
                [zone, "MASTER", serial, "NOC:%s" % uuid]
            )
            zone_id = self.execute(
                "SELECT id "
                "FROM DOMAINS "
                "WHERE name = ?",
                [zone]
            )[0][0]
            existing = set()
        # Deleted records
        recs = set(records)
        for name, type, content, ttl, prio in existing - recs:
            self.execute(
                "DELETE FROM RECORDS "
                "WHERE "
                "   domain_id = ? "
                "   AND name = ? "
                "   AND type = ? "
                "   AND content = ?",
                [zone_id, name, type, content])
        # New records
        for name, type, content, ttl, prio in recs - existing:
            self.execute(
                "INSERT INTO RECORDS(domain_id, name, type, content,"
                "ttl, prio, change_date)"
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                [zone_id, name, type, content, ttl, prio, serial])
        self.execute("COMMIT")

    def delete_zone(self, uuid):
        acc = "NOC:%s" % uuid
        data = self.execute(
            "SELECT id, name "
            "FROM DOMAINS "
            "WHERE "
            "    account = ?",
            [acc]
        )
        if data:
            zone_id, name = data[0]
            self.logger.info("Deleting zone %s", name)
            self.execute(
                "DELETE FROM RECORDS WHERE domain_id = ?",
                [zone_id]
            )
            self.execute(
                "DELETE FROM DOMAINS WHERE id = ?",
                [zone_id]
            )
        self.execute("COMMIT")
