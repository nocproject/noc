
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        db.delete_column("dns_dnsserver","type_id")
        db.delete_table("dns_dnsservertype")
    
    def backwards(self):
        raise Exception("No backwards migration")
