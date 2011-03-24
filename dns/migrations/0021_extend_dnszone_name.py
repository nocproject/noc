# -*- coding: utf-8 -*-

from south.db import db

class Migration:
    
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER name TYPE VARCHAR(256)")
    
    def backwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER name TYPE VARCHAR(64)")
    
