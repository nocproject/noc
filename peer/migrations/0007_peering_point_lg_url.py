
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.add_column("peer_peeringpoint","lg_rcmd",models.CharField("LG RCMD Url",max_length=128,blank=True,null=True))
    
    def backwards(self):
        db.delete_column("peer_peeringpoint","lg_rcmd")
