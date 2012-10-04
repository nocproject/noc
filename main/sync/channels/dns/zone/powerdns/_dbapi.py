# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract Python DBAPI channel
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.sync.channel import Channel


class PowerDNSDBAPIChannel(Channel):
    """
    Abstract DBAPI SQL channel. Used in superclasses
    """
    def __init__(self, daemon, channel, name, config):
        super(PowerDNSDBAPIChannel, self).__init__(
            daemon, channel, name, config)
        self.databases = self.get_databases(config)
        if not self.databases:
            self.die("No databases set")
        self.account = config.get("account", "NOC")

    def get_database(self, db_string):
        """
        Get database connection. Must be overriden
        :param db_string: database connection string
        :return: database connection object
        """
        raise NotImplementedError()

    def get_databases(self, config):
        r = []
        for c in config:
            if c == "database" or c.startswith("database."):
                try:
                    r += [self.get_database(config[c])]
                except Exception, why:
                    self.die(str(why).strip())
        return r

    def normalized_records(self, records):
        for name, type, content, ttl, prio in records:
            if name.endswith("."):
                name = name[:-1]
            if (type in ("NS", "MX", "CNAME") and
                content.endswith(".")):
                content = content[:-1]
            yield name, type, content, ttl, prio

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
            c.execute("""
                SELECT id, name, notified_serial
                FROM domains
                WHERE account = %s""", [self.account])
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
                if seen[name] != items[name]:
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
        serial = data["serial"]
        type = "MASTER"
        records = set(self.normalized_records(data["records"]))  # (name, type, content, ttl, priority)
        for cn in self.databases:
            # Synchronize zone
            c = cn.cursor()
            c.execute("BEGIN")
            c.execute("""
            SELECT id, type, notified_serial, account
            FROM domains
            WHERE name = %s
            """, [object])
            r = c.fetchone()
            if not r:
                # Create new zone
                self.info("Creating new zone: %s" % object)
                c.execute("""
                INSERT INTO domains(name, type, notified_serial, account)
                VALUES(%s, %s, %s, %s)
                """, [object, type, serial, self.account])
                c.execute("SELECT id FROM domains WHERE name = %s",
                    [object])
                domain_id, = c.fetchone()
            else:
                # Check for changes
                domain_id, d_type, notified_serial, account = r
                if account != self.account:
                    self.info("%s is provisioned by other account (%s)" % (
                        object, account))
                    return  # Provisioned by other source
                changes = []
                if type != d_type:
                    changes = [("type", type)]
                if serial != notified_serial:
                    changes = [("notified_serial", serial)]
                if changes:
                    # Zone changed
                    self.info("Changing zone %s: %s" % (object, changes))
                    expr = []
                    values = []
                    for f, v in changes:
                        expr += ["%s = %%s" % f]
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
                    ttl, prio, change_date)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                """, [domain_id, name, type, content, ttl, prio, serial])
                new += 1
            self.info("%s summary: %d new/ %d removed" % (
                object, new, removed))
            c.execute("COMMIT")
