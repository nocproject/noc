##
## Remove DNSZoneProfile.zone_ns_list, create necessary DNSServerObjects and links between zones and profiles
##
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        t=DNSServerType.objects.get(name="BINDv9")
        nses={}
        for p in DNSZoneProfile.objects.all():
            for n in [x.strip() for x in p.zone_ns_list.split(",")]:
                if n not in nses:
                    try:
                        ns=DNSServer.objects.get(name=n)
                        nses[n]=ns
                    except DNSServer.DoesNotExist:
                        ns=DNSServer(name=n,type=t)
                        ns.save()
                        nses[n]=ns
                    p.ns_servers.add(nses[n])
                    
        db.delete_column("dns_dnszoneprofile","zone_ns_list")
    
    def backwards(self):
        db.add_column("dns_dnszoneprofile","zone_ns_list",models.CharField("NS list",max_length=64))
        for p in DNSZoneProfile.objects.all():
            p.zone_ns_list=",".join([n.name for n in p.ns_servers.all()])
            p.save()