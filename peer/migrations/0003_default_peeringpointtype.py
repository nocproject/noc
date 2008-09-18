
from south.db import db
from noc.peer.models import *

LEGACY=[
    ("Cisco","Cisco.IOS"),
    ("Juniper","Juniper.JUNOS"),
    ("IOS","Cisco.IOS"),
    ("JUNOS","Juniper.JUNOS"),
]
TYPES=["Cisco.IOS","Juniper.JUNOS"]
class Migration:
    def forwards(self):
        print "Migrating peering point type names"
        for f,t in LEGACY:
            try:
                p=PeeringPointType.objects.get(name=f)
                print "%s -> %s"%(f,t)
                p.name=t
                p.save()
            except PeeringPointType.DoesNotExist:
                pass
        for t in TYPES:
            try:
                PeeringPointType.objects.get(name=t)
            except:
                print "Creating: %s"%t
                p=PeeringPointType(name=t)
                p.save()
    
    def backwards(self):
        for t in TYPES:
            try:
                p=PeeringPointType.objects.get(name=t)
                p.delete()
            except:
                pass
