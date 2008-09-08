
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        db.add_column("dns_dnszonerecordtype","is_visible",models.BooleanField("Is Visible?",default=True))
    
    def backwards(self):
        db.delete_column("dns_dnszonerecordtype","is_visible")
