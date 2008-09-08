
from south.db import db
from noc.peer.models import *

TYPES=["Cisco","Juniper"]
class Migration:
    def forwards(self):
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
