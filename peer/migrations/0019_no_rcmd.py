
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.delete_column("peer_peeringpoint","lg_rcmd")
        db.delete_column("peer_peeringpoint","provision_rcmd")
    
    def backwards(self):
        "Write your backwards migration here"
