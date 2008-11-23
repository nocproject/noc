
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        db.add_column("dns_dnszonerecordtype","validation",models.CharField("Validation",max_length=256,blank=True,null=True))
    
    def backwards(self):
        db.delete_column("dns_dnszonerecordtype","validation")
