##
## Remove DNSZoneProfile.zone_ns_list, create necessary DNSServerObjects and links between zones and profiles
##
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        t=DNSServerType.objects.get(name="BINDv9")
        t_id=t.id
        for p_id,zl in db.execute("SELECT id,zone_ns_list FROM dns_dnszoneprofile"):
            for n in [x.strip() for x in zl.split(",")]:
                if db.execute("SELECT COUNT(*) FROM dns_dnsserver WHERE name=%s",[n])[0][0]==0:
                    db.execute("INSERT INTO dns_dnsserver(name,type_id) values (%s,%s)",[n,t_id])
                db.execute("INSERT INTO dns_dnszoneprofile_ns_servers(dnszoneprofile_id,dnsserver_id) SELECT %s,id FROM dns_dnsserver WHERE name=%s",
                    [p_id,n])
                    
        db.delete_column("dns_dnszoneprofile","zone_ns_list")
    
    def backwards(self):
        db.add_column("dns_dnszoneprofile","zone_ns_list",models.CharField("NS list",max_length=64))
        for p in DNSZoneProfile.objects.all():
            p.zone_ns_list=",".join([n.name for n in p.ns_servers.all()])
            p.save()