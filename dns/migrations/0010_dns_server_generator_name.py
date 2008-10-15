
from south.db import db
from noc.dns.models import *

class Migration:
    def forwards(self):
        types={}
        for t_id,name in db.execute("SELECT id,name FROM dns_dnsservertype"):
            types[t_id]=name
        db.add_column("dns_dnsserver","generator_name",models.CharField("Generator",max_length=32,default="BINDv9"))
        for s_id,t_id in db.execute("SELECT id,type_id FROM dns_dnsserver"):
            db.execute("UPDATE dns_dnsserver SET generator_name=%s WHERE id=%s",[types[t_id],s_id])
    
    def backwards(self):
        raise "No backwards way"