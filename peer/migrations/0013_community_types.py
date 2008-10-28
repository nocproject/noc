
from south.db import db
from noc.peer.models import *

NAMES=[
    "Other Normal",
    "Other Extended"
]

class Migration:
    
    def forwards(self):
        for n in NAMES:
            if db.execute("SELECT COUNT(*) FROM peer_communitytype WHERE name=%s",[n])[0][0]==0:
                db.execute("INSERT INTO peer_communitytype(name) VALUES(%s)",[n])
    
    def backwards(self):
        pass
