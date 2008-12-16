
from south.db import db
from noc.dns.models import *

class Migration:
        def forwards(self):
            db.add_column("dns_dnsserver","provisioning",models.CharField("Provisioning",max_length=128,blank=True,null=True))
            for ns in DNSServer.objects.all():
                ns.provisioning="%%(rsync)s -av --delete * /tmp/dns"
                ns.save()

        def backwards(self):
            db.delete_column("dns_dnsserver","provisioning")
