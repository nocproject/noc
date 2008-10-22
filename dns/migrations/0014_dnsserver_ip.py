
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        db.add_column("dns_dnsserver","ip",models.IPAddressField("IP",null=True,blank=True))
    
    def backwards(self):
        db.delete_column("dns_dnsserver","ip")
