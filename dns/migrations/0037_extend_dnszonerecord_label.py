# -*- coding: utf-8 -*-

from south.db import db

class Migration:
    
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(64)")
    
    def backwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(32)")
