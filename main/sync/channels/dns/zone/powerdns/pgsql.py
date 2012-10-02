# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PowerDNS/PostgreSQL sync backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import psycopg2
## NOC modules
from noc.main.sync.channel import Channel


class PowerDNSPgSQLChannel(Channel):
    """
    Config example:

    [dns/zone/ch1]
    type = powerdns/pgsql
    enabled = true
    database = dbname=dns user=user
    """
    def __init__(self, daemon, channel, name, config):
        super(PowerDNSPgSQLChannel, self).__init__(
            daemon, channel, name, config)
        self.databases = self.get_databases(config)
        if not self.databases:
            self.die("No databases set")

    def get_databases(self, config):
        r = []
        for c in config:
            if c == "database" or c.startswith("database."):
                try:
                    r += [psycopg2.connect(config[c])]
                except psycopg2.OperationalError, why:
                    self.die(str(why).strip())
        return r

    def on_list(self, items):
        """
        :param items: Dict of name -> version
        :return:
        """
        remote = set(items)
        missed = set()
        # Check existing records
        for cn in self.databases:
            c = cn.cursor()
            c.execute("BEGIN")
            c.execute("SELECT id, name, notified_serial FROM domains")
            seen = {}  # name -> version
            for id, name, serial in c.fetchall():
                if name not in remote:
                    self.info("Removing stale domain %s" % name)
                    # Remove stale domain
                    c.execute("DELETE FROM records WHERE domain_id = %s",
                        [id])
                    c.execute("DELETE FROM domains WHERE id = %s", [id])
                    continue
                seen[name] = serial
            # Update missed list
            missed |= remote - set(seen)
            # Update missed list with mismatched serials
            for name in seen:
                if seen[name] != int(items[name]):
                    # Version mismatch
                    missed.add(name)
            c.execute("COMMIT")
        # Request missed domains
        if missed:
            self.verify(missed)

    def on_verify(self, object, data):
        """
        :param object: zone name
        :param data: dict of
            *serial* - Zone serial
            *records* - list of (name, type, content, ttl, priority)
        :return:
        """
        serial = int(data["serial"])
        type = "MASTER"
        records = set(tuple(r) for r in data["records"])  # (name, type, content, ttl, priority)
        for cn in self.databases:
            # Synchronize zone
            c = cn.cursor()
            c.execute("BEGIN")
            c.execute("""
            SELECT id, "type", notified_serial
            FROM domains
            WHERE name = %s
            """, [object])
            r = c.fetchone()
            if not r:
                # Create new zone
                self.info("Creating new zone: %s" % object)
                c.execute("""
                INSERT INTO domains(name, "type", notified_serial)
                VALUES(%s, %s, %s)
                """, [object, type, serial])
                c.execute("SELECT id FROM domains WHERE name = %s",
                    [object])
                domain_id, = c.fetchone()
            else:
                # Check for changes
                domain_id, d_type, notified_serial = r
                changes = []
                if type != d_type:
                    changes = [("\"type\"", type)]
                if serial != notified_serial:
                    changes = [("notified_serial", serial)]
                if changes:
                    # Zone changed
                    self.info("Changing zone %s: %s" % (object, changes))
                    expr = []
                    values = []
                    for f, v in changes:
                        expr += ["\"%s\" = %%s" % f]
                        values += [v]
                    expr = ", ".join(expr)
                    values += [domain_id]
                    c.execute("""
                    UPDATE domains
                    SET
                        %s
                    WHERE id = %%s
                    """ % expr, values)
            # Synchronize records
            c.execute("""
            SELECT name, type, content, ttl, prio
            FROM records
            WHERE domain_id = %s
            """, [domain_id])
            existing = set(c.fetchall())
            new = 0
            removed = 0
            # Deleted records
            for name, type, content, ttl, prio in existing - records:
                self.info("%s: Removing RR %s %s %s" % (
                    object, name, type, content))
                c.execute("""
                DELETE FROM records
                WHERE
                    domain_id = %s
                    AND name = %s
                    AND type = %s
                    AND content = %s
                """, [domain_id, name, type, content])
                removed += 1
            # New records
            for name, type, content, ttl, prio in records - existing:
                self.info("%s: Creating RR %s %s %s" % (
                    object, name, type, content))
                c.execute("""
                INSERT INTO records(domain_id, name, type, content,
                    ttl, prio)
                VALUES(%s, %s, %s, %s, %s, %s)
                """, [domain_id, name, type, content, ttl, prio])
                new += 1
            self.info("%s summary: %d new/ %d removed" % (
                object, new, removed))
            c.execute("COMMIT")
