# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER serial DROP DEFAULT")
        db.execute("ALTER TABLE dns_dnszone ALTER serial TYPE INTEGER USING serial::integer")
        db.execute("ALTER TABLE dns_dnszone ALTER serial SET DEFAULT 0")
        db.execute("ALTER TABLE dns_dnszone ALTER serial SET NOT NULL")

    def backwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER serial DROP DEFAULT")
        db.execute("ALTER TABLE dns_dnszone ALTER serial TYPE VARCHAR(10)")
        db.execute("ALTER TABLE dns_dnszone ALTER serial SET DEFAULT '0000000000'")
        db.execute("ALTER TABLE dns_dnszone ALTER serial SET NOT NULL")
