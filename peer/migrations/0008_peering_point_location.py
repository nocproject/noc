
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.add_column("peer_peeringpoint","location",models.CharField("Location",max_length=64,blank=True,null=True))
        
    
    def backwards(self):
        db.delete_column("peer_peeringpoint","location")
