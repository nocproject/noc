
from south.db import db
from noc.dns.models import *

NAME="BINDv9"
class Migration:
    def forwards(self):
        try:
            p=DNSServerType.objects.get(name=NAME)
        except DNSServerType.DoesNotExist:
            p=DNSServerType(name=NAME)
            p.save()
    
    def backwards(self):
        try:
            p=DNSServerType.objects.get(name=NAME)
            p.delete()
        except DNSServerType.DoesNotExist:
            pass
