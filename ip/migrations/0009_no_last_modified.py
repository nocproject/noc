# -*- coding: utf-8 -*-

from south.db import db

class Migration:
    
    def forwards(self):
        db.delete_column("ip_ipv4block","modified_by_id")
        db.delete_column("ip_ipv4block","last_modified")
        db.delete_column("ip_ipv4address","modified_by_id")
        db.delete_column("ip_ipv4address","last_modified")
        
    def backwards(self):
        pass
