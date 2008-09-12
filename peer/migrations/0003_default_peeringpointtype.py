
from south.db import db
from noc.peer.models import *

LEGACY=[
    ("Cisco","IOS"),
    ("Juniper","JUNOS")
]
TYPES=["IOS","JUNOS"]
class Migration:
    def forwards(self):
        for f,t in LEGACY:
            try:
                p=PeeringPointType.objects.get(name=f)
                p.name=t
                p.save()
            except PeeringPointType.DoesNotExist:
                pass
        for t in TYPES:
            try:
                PeeringPointType.objects.get(name=t)
            except:
                p=PeeringPointType(name=t)
                p.save()
    
    def backwards(self):
        for t in TYPES:
            try:
                p=PeeringPointType.objects.get(name=t)
                p.delete()
            except:
                pass
